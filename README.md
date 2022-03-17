# automx2docker

The python package [automx2](https://github.com/rseichter/automx2) helps users to simplify the configuration of their
email clients. It is packaged as a Docker image for an effortless setup process.

## Usage

The automx2docker image can be set up with the orchestrator of your choice. Here's an example of how to use
automx2docker with docker-compose. As a proxy server [traefik](https://doc.traefik.io/traefik/) is utilized.

```yaml
  autoconfig:
    image: ghcr.io/lukwebsforge/automx2docker:latest
    environment:
      PROXY_COUNT: '1'
      PROVIDER_NAME: 'Sky Mail Ltd.'
      PROVIDER_SHORTNAME: 'Sky Mail'
      DOMAINS: 'sky-mail.com,sky-post.com'
      # IMAP
      IMAP_HOST: 'imap.sky-mail.com'
      IMAP_PORT: '993'
      IMAP_SOCKET: 'SSL'
      # SMTP
      SMTP_HOST: 'smtp.sky-mail.com'
      SMTP_PORT: '465'
      SMTP_SOCKET: 'SSL'
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.autoconfig.rule=
      HeadersRegexp(`{subdomain:(autoconfig|autodiscovery)}.{domain:(sky-mail|sky-post)}.com`) && 
      Path(`/mobileconfig/`, `/mail/config-v1.1.xml`, `/AutoDiscover/AutoDiscover.xml`, `/autodiscover/autodiscover.xml`)"
```

## Configuration

Configuration of the image is possible via environment variables. They are inspired by the
project [autodiscover-email-settings](https://github.com/Monogramm/autodiscover-email-settings).

| Variable             | Description                                                      | Example                   | Required |
|----------------------|------------------------------------------------------------------|---------------------------|----------|
| `PROXY_COUNT`        | The number of proxy servers between the container and the client | 1                         | Yes      |
| `PROVIDER_NAME`      | The long name of the email provider                              | Sky Mail Ltd.             | Yes*     |
| `PROVIDER_SHORTNAME` | The short name of the email provider                             | Sky Mail                  | Yes*     |
| `DOMAINS`            | A comma-separated list of domains names                          | sky-mail.com,sky-post.com | Yes*     |
| `IMAP_HOST`          | The domain for the IMAP server (Leave empty to disable)          | imap.sky-mail.com         | No       |
| `IMAP_PORT`          | The port of the IMAP server (SSL = 993, STARTTLS = 143)          | 993                       | No       |
| `IMAP_SOCKET`        | The mechanism for encryption (Values: SSL, STARTTLS)             | SSL                       | No       |
| `POP_HOST`           | The domain for the POP3 server (Leave empty to disable)          | pop.sky-mail.com          | No       |
| `POP_PORT`           | The port of the POP server (SSL = 995, STARTTLS = 110)           | 995                       | No       |
| `POP_SOCKET`         | The mechanism for encryption (Values: SSL, STARTTLS)             | SSL                       | No       |
| `SMTP_HOST`          | The domain for the SMTP server (Leave empty to disable)          | smtp.sky-mail.com         | No       |
| `SMTP_PORT`          | The port of the SMTP server (SSL = 465, STARTTLS = 587)          | 465                       | No       |
| `SMTP_SOCKET`        | The mechanism for encryption (Values: SSL, STARTTLS)             | SSL                       | No       |

`*` Not required if a custom SQL script is set.

If environment variables are not powerful enough, it is also possible to configure automx2 using a custom SQL script.
The script has be mounted at the path `/data/custom.sql`. In this case only the environment variable `PROXY_COUNT` is
required. The values of all other environment variables are ignored.

The custom SQL script can be utilized for enabling [LDAP support](https://rseichter.github.io/automx2/#ldap). To
understand all available options, you have to take a look at the code of automx2. The
files [`contrib/sqlite-generate.sh`](https://github.com/rseichter/automx2/blob/master/contrib/sqlite-generate.sh) and
[`automx2/model.py`](https://github.com/rseichter/automx2/blob/master/automx2/model.py) are good starting points.

## Proxy

You should put a proxy server in front of the automx2docker container.

The proxy server should route the subdomains `autoconfig` and `autodiscover` to the container. Furthermore, it should
block the path `/initdb/` to prevent database changes from outside.

Example configurations can be found in this repository and on the automx2 website. They may have to be adapted to your
system.

* [traefik](examples/docker-compose.yml)
* [NGINX](https://rseichter.github.io/automx2/#nginx)
* [Apache](https://rseichter.github.io/automx2/#apache)
