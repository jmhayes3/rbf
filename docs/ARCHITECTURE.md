# Architecture

Uses a distributed architecture based on established ZMQ patterns. Specifically, the following patterns are used:
    - Clone pattern - reliable pub-sub - eventually-consistent state using shared key-value store across worker nodes.
    - Binary Star pattern - reliable failover for server nodes.