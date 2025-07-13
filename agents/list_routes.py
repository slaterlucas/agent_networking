from alice_agent import app

for route in app.routes:
    print(route.path, route.methods)
    if hasattr(route, 'app'):
        # If this is a mounted app, list its routes too
        for subroute in route.app.routes:
            print('  ', subroute.path, subroute.methods) 