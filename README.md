# automx2-docker

The python package [automx2](https://github.com/rseichter/automx2) helps users to simplify email configuration in their
mail clients. The functionality of the package can be used with Docker.

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

If environment variables are not powerful enough, it is also possible to configure automx2 via a custom SQL script. The
script has be mounted at the path `/data/custom.sql`. In this case the environment variable `PROXY_COUNT` only has to be
set. The values of all other environment variables are ignored.

The custom SQL script can be utilized for enabling [LDAP support](https://rseichter.github.io/automx2/#ldap). To
understand all available options, you have to take a look at the code. The
files [`contrib/sqlite-generate.sh`](https://github.com/rseichter/automx2/blob/master/contrib/sqlite-generate.sh) and
[`automx2/model.py`](https://github.com/rseichter/automx2/blob/master/automx2/model.py) are good starting points.

## Proxy

You should put a proxy server in front of the automx2 container.

The proxy server should route the subdomains `autoconfig` and `autodiscover` to the container. Furthermore, it should
block the access to the path `/initdb/` to prevent database changes from outside.

Example configurations can be found in this repository and on the automx2 website:

* [traefik](examples/docker-compose.yml)
* [NGINX](https://rseichter.github.io/automx2/#nginx)
* [Apache](https://rseichter.github.io/automx2/#apache)