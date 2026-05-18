from world import World
from config import SimulationConfig
import json
import asyncio
import websockets
from websockets.server import WebSocketServerProtocol
from vector2D import vector2D
from agents import Boid, Predator, Food

class SimulationServer:
    """
    A class to bridge the Python simulation engine with the browser
    The server will use asyncio event loop and the websockets library
    """
    def __init__(self, config: SimulationConfig, host: str = "127.0.0.1", port: int = 8333):
        self.config = config
        # Websocket host and port
        self.host = host
        self.port = port
        # World instance
        self.world = World(self.config)
        # Track connected clients
        self._clients = set()

    # An async function can be paused at any await point in its code, allowing other alt tasks to be run
    async def _simulation_loop(self):
        """
        An async method that will run forever
            - Call the world tick
            - Serialise the snapshot in JSON
            - Broadcast it to all clients
            - Then pause simulation and allow other tasks to run for a bit 
        """
        while True:
            # Get the snapshot of the world tick
            self.world.tick(self.config)
            # Serialise the snapshot as JSON
            world_snap = json.dumps(self.world.snapshot())

            # Broadcast this snapshot to all clients
            # await - pauses the exec of a task until the result of another task or operation is ready
            await asyncio.gather(
                *(client.send(world_snap) for client in list(self._clients)),
                return_exceptions=True
            )

            # Yielding the event loop by the tick rate delay
            await asyncio.sleep(self.config.tick_rate)

    async def _handle_messages(self, ws: WebSocketServerProtocol):
        """
        Async method that listens for incoming JSON messages from a single client
        Parses each message and handle two types:
            - type: 'config' -> The message contains key-value pairs matching config field names
                    Updates the corresponding fields on the SimulationConfig object
                    This allows browser sliders to change behaviour weights in real time

            - type: 'spawn' -> The message contains entity ('boid', 'predator', or 'food'), x, and y
                    Creates the appropriate agent at that position and adds it to the world
        """
        try:
            # Loop forever listening for messages from this client
            async for raw in ws:
                # Parse raw string as JSON
                parsed_msg = json.loads(raw)
                # Check the type field of the parsed message
                if parsed_msg.get("type") == "config":
                    # Loop through the key-value pairs and update the matching fields
                    for key, value in parsed_msg.items():
                        if key != "type":
                            setattr(self.config, key, value)
                elif parsed_msg.get("type") == "spawn":        
                    # Read the entity, x, and y fields to create the appropriate agent
                    spawn_entity = parsed_msg.get("entity")
                    spawn_x = parsed_msg.get("x")
                    spawn_y = parsed_msg.get("y")

                    # Create a vector from the x and y
                    spawn_vector = vector2D(spawn_x, spawn_y)

                    # Append the new entity
                    if spawn_entity == "boid":
                        # Create a velocity
                        spawn_velocity = vector2D.random_unit() * (self.config.boid_max_speed * 0.5)
                        # Append new boid to world list of boids
                        self.world.boids.append(Boid(spawn_vector, spawn_velocity, self.config))
                    elif spawn_entity == "predator":
                        # Create a velocity
                        spawn_velocity = vector2D.random_unit() * (self.config.predator_max_speed * 0.5)
                        # Append new predator to world list of predators
                        self.world.predators.append(Predator(spawn_vector, spawn_velocity, self.config))
                    elif spawn_entity == "food":
                        # Append food to world list of food sources
                        self.world.food.append(Food(spawn_vector, self.config))
        # If client disconnected then the exception is caught and method is ended cleanly
        except websockets.ConnectionClosed:
            pass

    async def _ws_handler(self, ws: WebSocketServerProtocol):
        """Registers a client when they connect and removes them when they disconnect"""
        # Add the client when they connect
        self._clients.add(ws)
        # Listen for their messages
        try:
            await self._handle_messages(ws)
        # Remove the client when they disconnect
        finally:
            self._clients.discard(ws)

    async def run(self):
        """Starts the WebSocket server and the simulation loop"""
        # Start the WebSocket server as an async context manager
        async with websockets.serve(self._ws_handler, self.host, self.port):
            # Run the simulation forever
            await self._simulation_loop()