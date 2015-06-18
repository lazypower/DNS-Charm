# AWS Route 53 Provider Integration

### Warnings of caution

It's highly recommended you setup an AWS IAM account, with the proper sandboxed 
ARN rulests to only access the domain in which you are going to be binding to the
DNS charm. This will prevent addtional damage should the credentials ever become
compromised, or a nasty bug creep into the code. Please use your best judgement
when using this integration.

### Prerequisits

You must provide the charm's `provider_keys` directive with at least the 2 keys
bound to an account with authorization to access and modify Rt53 resources.

    juju set dns provider="rt53"
    juju set dns provider_keys="AWS_ACCESS_KEY_ID|1234 AWS_SECRET_ACCESS_KEY|abc123def"

By setting the provider to rt53, and providing the requisite Access keys you are
now ready to start the integration of your Juju Environment w/ AWS Rt53 domains.

The charm will do its best attempt to validate that it has the proper access
before making any modifications. But please note, that this will assume full
control over any requested resources. Meaning, whichever domain you assign to
the charm - the charm will overwrite, update, and remove DNS records as if you
had made the request yourself. This is fully managed DNS provided by Juju.

Changes you make outside of this charm will **not** persist through an update.


### Currently Supported Record Types

The record types this provider will accept are marked in the
`contrib/rt53/provider.py` initializer. This helps cut down on attempting to
make API calls we're not sure how to handle.

    self.record_types = ['A', 'CNAME']

To date, we support the most common DNS record entries youll encounter. Should
you need another, PR's are welcome - but you'll need to include a test that
stubs the AWS Rt53 API with a fixture to illustrate usage.

### Known Caveats

The DNS charm does not actively reconfigure from one provider to another. This
feat of configuration requires revisiting the core logic of the charm and
implementing additional calls to determine if the underlying DNS provider has
changed.

When switching providers. you have two options presently:

- Attach to the charm over debug-hooks during an event, and manually run the
  install/config-changed hooks.  `hooks/install  && hooks/config-changed`

- Redeploy the service


### Bugs / Feature Requests

Please file any/all bugs and feature requests against the dns-charm
[issue tracker](https://github.com/chuckbutler/dns-charm/issues)
on github, and ensure you call out the issue is with the `rt53` provider.


