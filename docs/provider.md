# Providers

### Purpose:

Provider's are essentially service wrappers that expose a common interface to interacting with them. [The DNS Charm spec](spec-document.pdf) has a simple and straight forward purpose: to add, remove, or update a pointer/informational record against a given domain. We can achieve communication with any provider through this simple exposed set of methods and consume new services as they emerge.

## Requirements for upstream inclusion:

All providers must meet the following criteria for addition:

- fully unit tested
- documented in docs/providers/*providername*.md
- peer reviewed and acknowledged for merging
- Self contained, and rely only on itself for method inclusion
- Implement the methods outlined in [README.md](README.md)

## Adding A Provider:

The charm has a `contrib` directory that warehouses all provider code. These are ideally in Python and will consume as few resources as possible to communicate with the provider to ease installation in 'offline' or 'limited connectivity' environments.

Resources that come from locations such as PyPi should be noted in the provider's documentation to ensure anyone deploying to a limited connectivity environment can allocate all required source packages for 'offline installation'. The charm will be forked locally and deployed with files placed in the 'files/provider' directory. All installation logic is then to be handled by the given providers installation routine.

### Note: 

In the given examples, we will assume there is a DNS provider named *GoCheap* with a WebAPI, and a wrapping python library named *GoCheapLib*

### Create the Directory Structure

    mkdir contrib/gocheap
    touch contrib/gocheap/install.py
    touch contrib/gocheap/provider.py
    touch contrib/gocheap/requirements.txt    
    touch contrib/tests/gocheap_test.py

### Setup Dependencies
Add any PIP requirements required for installation into **provider/requirements.txt**. 

In our case, requirements.txt will look like the following:

    gocheaplib

### Add Provider Code

In provider.py, you need to create a scaffolded provider. In terms of example, you may reference the `contrib/bind/provider.py` provider code.

Your Provider class should **always** be Provider(object) - as the directory structure will deliniate the different providers. Allowing the charm hook wrappers to use inflection to infer the proper class methods to call.

An example skeleton provider.py file:

    class Provider(object):
    
        def ConfigChanged(self):
            pass
            
        def AddRecord(self):
            pass
        
        def RemoveRecord(self):
            pass
        
        def UpdateRecord(self):
            pass


From this skeleton, you are free to add whatever required models, classes, libraries, modules, and other requirements to integrate with your given provider. In terms of Setup with API Keys and ensuring they are kept together, there is a configuration variable: **provider_keys** that should hold the credentials in key|value form. EG: if your two API tokens are APIKey and APISecret, they would look similar to the following:

    APIKey|1234567 APISecret|foobar
    
Space separated, and key/value separated with a Pipe character   "|"

