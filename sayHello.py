def sayHello(to = None):
    if to:
        print("Hello, %s!" % to)
    else:
        print("Hello!")

sayHello()
sayHello(to = 'Jason')