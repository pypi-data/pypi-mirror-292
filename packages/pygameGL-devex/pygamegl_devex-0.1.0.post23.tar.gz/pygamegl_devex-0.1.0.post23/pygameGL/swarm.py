def load_SwarmECS():
    try:
        import swarm as swarmECS
    except ImportError as err:
        print(f"Error Importing Swarm-ECS: Please Install it with `pip install -U Swarm-ECS`\n{err}")
        return None
    
    return swarmECS
