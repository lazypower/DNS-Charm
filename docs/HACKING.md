# Getting Started Hacking on DNS as a Service

There are a few convenience methods setup for developers looking to get started.

    make setup
    make sync-charm-helpers
    
will ensure you've got all the required python packages to execute tests and begin working with the charm. Concidentally you'll notice this is included in the online installer of the charm. Therefore any environment you deploy to, you effectively have a working dev environment to work with.

### Make Targets

There are several targets in the makefile to assist in assuring your submission will be of high quality out of the box.

- make test_contrib 
- - Executes all tests against the providers. Providers are located in `contrib/<provider>`

- make lint
- - Executes all linting tests against the code in the project. Such as `charm proof` and `flake8`

- make test
- - Executes all hook and deployment tests contained in the charms `tests` directory

- make sync-charm-helpers
- - Fetches the latest copy of charm helpers, a library to assist charm developers in building charms rapidly. To learn more about Charm Helpers, see: [Charm Helpers LP project](https://launchpad.net/charm-helpers)


### Adding Providers

**See:** the spec document for provider specifics

Providers are to be implemented in the contrib/ directory under their own nested diretory structure. The only mandated file here is the provider.py file. It is a wrapping class for exposing the underlying service. EG: if you were to extend the charm and add bobs DNS service, you would place it in `contrib/bobs` and touch a provider.py that implemented the following methods:

- add_record
- remove_record
- config_changed

and add a `contrib/bobs/install.py` file with the installation routine. This should be self-calling so invoking an object will run the installation routine.


These are the only mandated method calls to fit within the plugin architecture. Ideally we would like these to be python, but if you have an interesting use case that is non-python, and can be embedded as is, submit a pull request!


### Submission Workflow

As you make changes, every change is to be code reviewed by a peer associated with the project prior to merging into the codebase. So the workflow from a purely GitHub oriented aspect would be the following:

1. Fork Charm
2. Add Feature or fix bug
3. Add Tests to validate feature/bug
4. Submit pull request against upstream charm
5. Implement any requested changes
6. Enjoy upstream code changes

Every pull request is quality gated and must meet the [Juju Charm Store Policy](https://juju.ubuntu.com/docs/authors-charm-policy.html)


