# await / pyawait

`await` is a tool that waits until TCP hosts and ports to be open.

It is useful for synchronizing the spin-up of interdependent services, such as linked docker containers.

This is yet another alternative to `wait-for-it.sh`.

## Why?

- extended functionality:
    - can be set few addresses at the same time (e.g. `-a host:port -a host:port ...`)
    - can be set polling interval (e.g. `-i 100ms`)
    - timeout/interval can be provided in many different time units (`ns,ms,s,m,h`)
- available as a binary file (size <1mb) without any dependencies
- available via `pip` for convenience
## Installation

Download executable binary:

`sh -c "NAME=await curl -o $NAME https://raw.githubusercontent.com/jackcvr/await/main/pyawait/await-$(uname -m) && chmod +x $NAME"`

or:

`pip install pyawait`

## Usage

```text
Usage: await [-t timeout] [-i interval] [-q] [-v] [-s=false] [-a host:port ...] [command [args]]

  -a value
    	Address to be waiting for, in the form 'host:port'
  -i duration
    	Interval between retries in format N{ns,ms,s,m,h} (default 1s)
  -q	Do not print anything (default false)
  -s	Strict mode: execute command after successful result only (default true)
  -t duration
    	Timeout in format N{ns,ms,s,m,h}, e.g. '5s' == 5 seconds. Zero for no timeout (default 0)
  -v	Be verbose (default false)
  command args
	Execute command with arguments after successful connection
```

## Examples

Wait 5 seconds for port 80 on `www.google.com`, and if it is available, echo the message `Google is up`:

```bash
$ await -t 5s -a www.google.com:80 echo "Google is up"
2024/08/23 12:34:32.156464 successfully connected to www.google.com:80
Google is up
```

You can provide few addresses at the same time.

Next command waits 2 seconds for www.google.com:80 and localhost:5000, checking them every 500 milliseconds
with disabled strict and enabled verbose mode:
```bash
$ await -t 2s -i 500ms -s=false -v -a www.google.com:80 -a localhost:5000 echo "Printed anyway"
2024/08/23 14:42:03.171442 dial tcp 127.0.0.1:5000: connect: connection refused
2024/08/23 14:42:03.248549 successfully connected to www.google.com:80
2024/08/23 14:42:03.682781 dial tcp 127.0.0.1:5000: connect: connection refused
2024/08/23 14:42:04.183945 dial tcp 127.0.0.1:5000: connect: connection refused
2024/08/23 14:42:04.686111 dial tcp 127.0.0.1:5000: connect: connection refused
2024/08/23 14:42:05.187927 dial tcp: lookup localhost: i/o timeout
timeout error
Printed anyway
```

## License

MIT