# ssh_from_env
What would you do if a device on which you've stored your private ssh key files, is lost, stolen or damaged?

This small script allows a (basic, slow) ssh log-in shell session to be created using Fabric and Paramiko, from a private ssh key stored in an environment variable. Services such as Hashicorp Vault can run scripts such as this one, passing them secrets as environment variables. This makes saving copies of private key files (whether temporary or permanent) on a local disk unnecessary.

I do not claim this is best practise.  Nor that it scales (vault services can be used to authenticate ssh certificates instead).  
This script is only intended to be a simple mitigation to loss, theft and damage of physical devices.

Users able to rely on managed physical copies of ssh key files, do not need this library at all.  For the rest of us, please note this not a hardened magic bullet to manage all your security issues.  Produce your own security model.  In particular this approach:
 a) delegates important security decisions to second and third parties, in no particular order: myself, my own infrastructure and dependency providers, and your chosen cloud vault service provider(s). This script is a trade off.  It is intended to make
 you less vulnerable to all your offices burning down or devices being stolen.  But as with moving anything from on-prem to the cloud,
 this is always at the cost of exposing you to others' vulnerabilities instead.
 b) the vault service(s) themselves must now be secured. By their very nature, credible providers have considered this at length, e.g. requiring password, and either a OTP or a recovery code (storing recovery codes on the devices instead of ssh key files, just shifts the
 problem to a different file, and adds only a little obscurity, not any extra security).



## Usage:
1) Create an account with a Vault provider with a CLI, e.g. Hashicorp Vault.  Install this provider's CLI. Copy the contents of the RSA 
private key file into a secret in this service (`ssh_from_env` will look for a secret called `SSH_KEY` by default).
2) `pipx install ssh_from_env`
3) Run the main entrypoint script, via the Vault provider's CLI, that
grants access to the secrets as environment variables.
```
hcp vault-secrets run -- ssh_from_env user@host (env_var_name=SSH_KEY)
```

## Alternatives

### Hard disk encryption or encrypted containers/volumes/partitions (e.g. Veracrypt)
#### Pros
 - Tested, established tools.
 - Simple to backup.
#### Cons
 - Not a mitigation by themselves alone for loss or damage (backups also required for this).
 - Extra passphrase to remember/store, or passphrase reuse required.
 - No audit trail
 - Credentials need to be entered each session to mount, as they are not remembered 
   (it could also be argued this is a "Con" of a Vault service).