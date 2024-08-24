# Pulumi Bare Metal

A Pulumi provider for provisioning bare-metal hosts.

## Build & test the boilerplate provider

1. Create a new Github CodeSpaces environment using this repository.
1. Open a terminal in the CodeSpaces environment.
1. Run `make build install` to build and install the provider.
1. Run `make gen_examples` to generate the example programs in `examples/` off of the source `examples/yaml` example program.
1. Run `make up` to run the example program in `examples/yaml`.
1. Run `make down` to tear down the example program.

## References

Other resources/examples for implementing providers:

* [Pulumi Command provider](https://github.com/pulumi/pulumi-command/blob/master/provider/pkg/provider/provider.go)
* [Pulumi Go Provider repository](https://github.com/pulumi/pulumi-go-provider)
