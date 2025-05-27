Scheduler Service


Failure Mode	                    Handling Strategy
Temporary Network Glitch	        Automatic retry with backoff (both connections and channels)
RabbitMQ Node Failure	            Rely on RabbitMQ cluster + client-side reconnection
Database Connection Loss	        Pause message processing until DB returns (while keeping messages unacked)
Message Processing Failure	        Dead Letter Exchange (DLX) + retry queue with TTL

