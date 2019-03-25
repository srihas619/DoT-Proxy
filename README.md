# DNS over TLS (DoT) Proxy

## Implementation

Core functionality is implemented using `socket` and `ssl` modules in Python.

Satisfies the requirement to handle single TCP DNS query over 53 port and relaying it to a `DNS over TLS server` 
over an encrypted connection. Sends the response to client.

A server is started on port 53 that listens to DNS queries over TCP. 
Once a query is received on the socket, socket is wrapped into an SSL context thats created with the ca.pem in our OS cert store.
This wrapped socket is sent to a `DNS over TLS`(DoT) server(Cloudflare's 1.1.1.1 in our case) with destination port as 853. 
Response from DoT server is relayed to the client via `socket.sendall`.

A `config.yml` is provided which takes a list of DoT servers and the server address to bind the socket.
This is parsed using `pyYaml`. These server(s) can be used as fallback option(s) to query when one of them fails.
This ensures High Availability(HA) for the proxy.

## Usage

### Building Image
Inside project root directory
```
$ docker build -t dot:1.0 .
```
### Starting container
```
$ docker run -d --name dot_proxy -v <full path to config.yml>:/app/config.yml -p 53:53 dot:1.0
```
### Running Dig query
```
$ dig google.com @127.0.0.1 +tcp

; <<>> DiG 9.10.6 <<>> google.com @127.0.0.1 +tcp
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 42503
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1452
; PAD: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 (".....................................................................")
;; QUESTION SECTION:
;google.com.			IN	A

;; ANSWER SECTION:
google.com.		134	IN	A	172.217.22.46

;; Query time: 74 msec
;; SERVER: 127.0.0.1#53(127.0.0.1)
;; WHEN: Mon Mar 25 09:35:57 EDT 2019
;; MSG SIZE  rcvd: 128

```

## Security Concerns

- Service depends on the DoT server's way of handling encryption
- Prone to TLS vulnerability and attacks as communication happens over TLS

## Microservice architecture

- This proxy can be deployed as a `side-car` container to any application pod in Kubernetes
- This can also be used as a proxy for a DNS server in any environment

## Other improvements

- This can be extended to handle multiple destination DoT servers in `config.yaml` with non-blocking and relaying the first successful response to the client.
- Handle concurrent requests
- Handle requests over UDP at the source
- Implementing DNS caching at the proxy level