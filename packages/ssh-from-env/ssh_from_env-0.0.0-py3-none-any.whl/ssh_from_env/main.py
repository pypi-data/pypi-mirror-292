import os
import io
import sys

import fabric
import paramiko

DEFAULT_ENV_VAR_NAME = 'SSH_KEY'

PREF = '-----BEGIN RSA PRIVATE KEY-----'
SUFF = '-----END RSA PRIVATE KEY-----'



def _start_ssh_session(user, host, env_var):
    # Hashicorp Vault strips out new lines from secrets.  Parmiko needs them restoring.
    # key_str = PREF + '\n' + env_var.removeprefix(PREF).removesuffix(SUFF).strip().replace(' ','\n') + '\n' + SUFF
    multi_line_key_str = env_var.removeprefix(PREF).removesuffix(SUFF).strip().replace(' ','\n')
    key_str = f'{PREF}\n{multi_line_key_str}\n{SUFF}'

    private_key = paramiko.RSAKey.from_private_key(io.StringIO(key_str))
    con = fabric.Connection(
        host=host,
        user=user,
        connect_kwargs={
            "pkey": private_key,
        },
    )
    # Fabric echoes stdin back as it assumes there is a Pseudo terminal.
    # TODO: Make a better repl.
    con.shell()


def main(args = sys.argv):

    #############################
    # TODO: Replace with argparse.  Or even more env variables.
    args = args[1:]
    #
    if not args:
        raise ValueError('Required: the user_name@host_uri to log in with. ')
    if '@' not in args[0]:
        raise ValueError(f'Invalid user_name@host_uri  Got: {args[0]}')
    user, __, host = args[0].partition('@')
    #
    env_var_name = args[1] if len(args) >= 2 else DEFAULT_ENV_VAR_NAME
    #############################

    env_var = os.getenv(env_var_name)

    if not env_var:
        raise EnvironmentError(
            f'No ssh key found in an environment variable called: {env_var_name}\n'
            f'Are you running ssh_from_env using e.g. "hcp vault-secrets run -- ssh_from_env user@host (env_var_name)"?'
            f'Default env variable name: {DEFAULT_ENV_VAR_NAME}'        
        )

    _start_ssh_session(user=user, host=host, env_var=env_var)


if __name__=='__main__':
    main()