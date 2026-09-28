*Please :star: this repo if you find it useful*

<p align="left"><br>
<a href="https://www.paypal.com/paypalme/techblogil?locale.x=he_IL" target="_blank"><img src="http://khrolenok.ru/support_paypal.png" alt="PayPal" width="250" height="48"></a> <!-- TODO: badge image URL is dead (404) -->
</p>


# Apprise API Bridge
## Single endpoint for sending notifications to multiple channels

[![License](https://img.shields.io/github/license/t0mer/apprise-api-bridge)](License)
[![Docker Pulls](https://img.shields.io/docker/pulls/techblog/apprise-api-bridge)](https://hub.docker.com/r/techblog/apprise-api-bridge)

Once in a while I need to send a notification from my environment. It can be an alert or an informational message.
So I created this project to help send these messages with minimal configuration and setup, and with the largest possible
number of supported notification channels.

Apprise API Bridge is a small [FastAPI](https://fastapi.tiangolo.com/) service that wraps the
[Apprise](https://github.com/caronc/apprise) library. You define named **groups** of Apprise URLs in a YAML file
(through the built-in web editor or the API), and then send a message to every channel in a group with a single
`GET` or `POST` request.

## Table of Contents
- [Features](#features)
- [How It Works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Using Apprise API Bridge](#using-apprise-api-bridge)
- [Supported Notifications](#supported-notifications)
- [Sending Notifications](#sending-notifications)
- [API Reference](#api-reference)
- [Security Notes](#security-notes)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Features
With Apprise API Bridge you can:
* Define notification groups (by importance, department, etc.), each with any number of Apprise notification URLs.
* Send a notification to all channels in a group using a `GET` or `POST` request.
* Edit the group configuration in a web-based YAML editor, or load and save it through the REST API.
* List the configured groups through the API (currently broken in the published image, see [Troubleshooting](#troubleshooting)).
* Browse interactive API documentation (Swagger UI at `/docs`, ReDoc at `/redoc`).
* Scrape Prometheus metrics for the HTTP server at `/metrics`.
* Run it as a multi-arch Docker image (`linux/amd64`, `linux/arm64`, `linux/arm/v7`).

## How It Works

```mermaid
flowchart LR
    Client["Script / service / curl"] -- "GET or POST /api/notifications/push<br/>group, title, message" --> Bridge["Apprise API Bridge<br/>(FastAPI, port 8080)"]
    UI["Web UI (YAML editor)"] -- "/api/config/load<br/>/api/config/save" --> Bridge
    Bridge -- "reads group URLs" --> Config[("config.yaml")]
    Bridge -- "Apprise" --> Channels["Telegram, Slack, Discord,<br/>email, MQTT, ..."]
```

1. `config.yaml` maps each group name to a list of Apprise URLs.
2. When a push request arrives, the service reads the URLs of the requested group, adds them to a new Apprise
   object, and calls `notify()` with the given title and message.
3. The configuration file is re-read on every request, so changes saved from the UI take effect immediately.

## Requirements
* Docker (recommended), or Python 3 to run from source.
* Accounts, tokens or webhooks for the notification services you want to use. See the
  [Apprise wiki](https://github.com/caronc/apprise/wiki) for the URL format of each service.

## Installation

### Docker
The image is published to Docker Hub as `techblog/apprise-api-bridge` (tags `latest` and the version number).

```bash
docker run -d --name appriseapi --restart always -p 8080:8080 techblog/apprise-api-bridge:latest
```

### Docker Compose
```yaml
services:
  appriseapi:
    image: techblog/apprise-api-bridge:latest
    container_name: appriseapi
    restart: always
    ports:
      - "8080:8080"
    # Optional: keep the configuration across container re-creation.
    # Create ./config.yaml on the host first (see "Configuration").
    # volumes:
    #   - ./config.yaml:/opt/app/config.yaml
```

### Build from source
```bash
git clone https://github.com/t0mer/apprise-api-bridge.git
cd apprise-api-bridge
docker build -t apprise-api-bridge .
docker run -d -p 8080:8080 apprise-api-bridge
```

To run without Docker, see [Development](#development).

## Configuration

### Runtime settings
The service has no environment variables or command-line flags. The following values are fixed in the code and image:

| Setting | Value | Notes |
|---------|-------|-------|
| Listening address | `0.0.0.0:8080` | Set in `app/app.py`. Map it to another host port with `-p <host-port>:8080`. |
| Configuration file | `/opt/app/config.yaml` (in the container) | Read relative to the working directory (`app/` when run from source). |
| Version | `app/VERSION` | Shown in the UI title and in the OpenAPI docs. |

The image does not declare a volume, so edits made in the UI are lost when the container is re-created. To keep them,
bind-mount a file to `/opt/app/config.yaml`. Create the file on the host before starting the container; otherwise
Docker creates a directory with that name and the service can't read it.

### Groups file (`config.yaml`)
Each top-level key is a group name, and its value is a list of [Apprise URLs](#supported-notifications). The file
shipped with the image contains an example `admins` group:

```yaml
#example
admins: #Group name
  - discord://webhook_id/webhook_token
  - msteams://TokenA/TokenB/TokenC/
  - slack://TokenA/TokenB/TokenC/Channel
  - mailgun://user@hostname/apikey/email1/email2/emailN
  - tgram://bottoken/ChatID
  - twitter://CKey/CSecret/AKey/ASecret
  - sns://{AccessKeyID}/{AccessKeySecret}/{Region}/+{PhoneNo}
```

Add as many groups as you need, for example:

```yaml
alerts:
  - tgram://bottoken/ChatID
  - mailto://user:password@gmail.com
info:
  - discord://webhook_id/webhook_token
```

## Using Apprise API Bridge
Now that you have installed Apprise API Bridge, it's time to give it a try.
Navigate to your server address (for example `http://<server>:8080`) and you should see the configuration screen,
which helps you configure the notification groups and channels.

* **Load Current Configuration** reloads `config.yaml` into the editor.
* **Update Configuration** saves the editor content back to `config.yaml`.

[![Apprise group configuration](https://raw.githubusercontent.com/t0mer/apprise-api-bridge/main/images/apprise%20api%20bridge%20-%20%20configuration.png?raw=true)](https://raw.githubusercontent.com/t0mer/apprise-api-bridge/main/images/apprise%20api%20bridge%20-%20%20configuration.png?raw=true)

## Supported Notifications
This section lists the services supported by the Apprise library. [Check out the wiki for more information on the supported modules](https://github.com/caronc/apprise/wiki).

### Popular Notification Services
The table below lists the services this tool supports, with example service URLs you need to use to take advantage of them. Click any of the services listed below to get more details on how to configure Apprise to access them.


| Notification Service | Service ID | Default Port | Example Syntax |
| -------------------- | ---------- | ------------ | -------------- |
| [Apprise API](https://github.com/caronc/apprise/wiki/Notify_apprise_api)  | apprise:// or apprises:// | (TCP) 80 or 443 | apprise://hostname/Token
| [AWS SES](https://github.com/caronc/apprise/wiki/Notify_ses)  | ses://   | (TCP) 443   | ses://user@domain/AccessKeyID/AccessSecretKey/RegionName<br/>ses://user@domain/AccessKeyID/AccessSecretKey/RegionName/email1/email2/emailN
| [Boxcar](https://github.com/caronc/apprise/wiki/Notify_boxcar)  | boxcar://   | (TCP) 443   | boxcar://hostname<br />boxcar://hostname/@tag<br/>boxcar://hostname/device_token<br />boxcar://hostname/device_token1/device_token2/device_tokenN<br />boxcar://hostname/@tag/@tag2/device_token
| [Discord](https://github.com/caronc/apprise/wiki/Notify_discord)  | discord://   | (TCP) 443   | discord://webhook_id/webhook_token<br />discord://avatar@webhook_id/webhook_token
| [Emby](https://github.com/caronc/apprise/wiki/Notify_emby)  | emby:// or embys:// | (TCP) 8096 | emby://user@hostname/<br />emby://user:password@hostname
| [Enigma2](https://github.com/caronc/apprise/wiki/Notify_enigma2)  | enigma2:// or enigma2s:// | (TCP) 80 or 443 | enigma2://hostname
| [Faast](https://github.com/caronc/apprise/wiki/Notify_faast) | faast://    | (TCP) 443    | faast://authorizationtoken
| [FCM](https://github.com/caronc/apprise/wiki/Notify_fcm) | fcm://    | (TCP) 443    | fcm://project@apikey/DEVICE_ID<br />fcm://project@apikey/#TOPIC<br/>fcm://project@apikey/DEVICE_ID1/#topic1/#topic2/DEVICE_ID2/
| [Flock](https://github.com/caronc/apprise/wiki/Notify_flock) | flock://    | (TCP) 443    | flock://token<br/>flock://botname@token<br/>flock://app_token/u:userid<br/>flock://app_token/g:channel_id<br/>flock://app_token/u:userid/g:channel_id
| [Gitter](https://github.com/caronc/apprise/wiki/Notify_gitter) | gitter://    | (TCP) 443    | gitter://token/room<br/>gitter://token/room1/room2/roomN
| [Google Chat](https://github.com/caronc/apprise/wiki/Notify_googlechat) | gchat://    | (TCP) 443    | gchat://workspace/key/token
| [Gotify](https://github.com/caronc/apprise/wiki/Notify_gotify) | gotify:// or gotifys://   | (TCP) 80 or 443    | gotify://hostname/token<br />gotifys://hostname/token?priority=high
| [Growl](https://github.com/caronc/apprise/wiki/Notify_growl)  | growl://   | (UDP) 23053   | growl://hostname<br />growl://hostname:portno<br />growl://password@hostname<br />growl://password@hostname:port<br />**Note**: you can also use the get parameter _version_ which can allow the growl request to behave using the older v1.x protocol. An example would look like: growl://hostname?version=1
| [Home Assistant](https://github.com/caronc/apprise/wiki/Notify_homeassistant)       | hassio:// or hassios://   | (TCP) 8123 or 443 | hassio://hostname/accesstoken<br />hassio://user@hostname/accesstoken<br />hassio://user:password@hostname:port/accesstoken<br />hassio://hostname/optional/path/accesstoken
| [IFTTT](https://github.com/caronc/apprise/wiki/Notify_ifttt) | ifttt://    | (TCP) 443    | ifttt://webhooksID/Event<br />ifttt://webhooksID/Event1/Event2/EventN<br/>ifttt://webhooksID/Event1/?+Key=Value<br/>ifttt://webhooksID/Event1/?-Key=value1
| [Join](https://github.com/caronc/apprise/wiki/Notify_join) | join://   | (TCP) 443    | join://apikey/device<br />join://apikey/device1/device2/deviceN/<br />join://apikey/group<br />join://apikey/groupA/groupB/groupN<br />join://apikey/DeviceA/groupA/groupN/DeviceN/
| [KODI](https://github.com/caronc/apprise/wiki/Notify_kodi) | kodi:// or kodis://    | (TCP) 8080 or 443   | kodi://hostname<br />kodi://user@hostname<br />kodi://user:password@hostname:port
| [Kumulos](https://github.com/caronc/apprise/wiki/Notify_kumulos) | kumulos:// | (TCP) 443 | kumulos://apikey/serverkey
| [LaMetric Time](https://github.com/caronc/apprise/wiki/Notify_lametric) | lametric:// | (TCP) 443 | lametric://apikey@device_ipaddr<br/>lametric://apikey@hostname:port<br/>lametric://client_id@client_secret
| [Mailgun](https://github.com/caronc/apprise/wiki/Notify_mailgun) | mailgun:// | (TCP) 443 | mailgun://user@hostname/apikey<br />mailgun://user@hostname/apikey/email<br />mailgun://user@hostname/apikey/email1/email2/emailN<br />mailgun://user@hostname/apikey/?name="From%20User"
| [Matrix](https://github.com/caronc/apprise/wiki/Notify_matrix) | matrix:// or matrixs://  | (TCP) 80 or 443 | matrix://hostname<br />matrix://user@hostname<br />matrixs://user:pass@hostname:port/#room_alias<br />matrixs://user:pass@hostname:port/!room_id<br />matrixs://user:pass@hostname:port/#room_alias/!room_id/#room2<br />matrixs://token@hostname:port/?webhook=matrix<br />matrix://user:token@hostname/?webhook=slack&format=markdown
| [Mattermost](https://github.com/caronc/apprise/wiki/Notify_mattermost) | mmost:// or mmosts:// | (TCP) 8065 | mmost://hostname/authkey<br />mmost://hostname:80/authkey<br />mmost://user@hostname:80/authkey<br />mmost://hostname/authkey?channel=channel<br />mmosts://hostname/authkey<br />mmosts://user@hostname/authkey<br />
| [Microsoft Teams](https://github.com/caronc/apprise/wiki/Notify_msteams) | msteams://  | (TCP) 443   | msteams://TokenA/TokenB/TokenC/
| [MQTT](https://github.com/caronc/apprise/wiki/Notify_mqtt) | mqtt://  or mqtts:// | (TCP) 1883 or 8883   | mqtt://hostname/topic<br />mqtt://user@hostname/topic<br />mqtts://user:pass@hostname:9883/topic
| [Nextcloud](https://github.com/caronc/apprise/wiki/Notify_nextcloud) | ncloud:// or nclouds:// | (TCP) 80 or 443 | ncloud://adminuser:pass@host/User<br/>nclouds://adminuser:pass@host/User1/User2/UserN
| [NextcloudTalk](https://github.com/caronc/apprise/wiki/Notify_nextcloudtalk) | nctalk:// or nctalks:// | (TCP) 80 or 443 | nctalk://user:pass@host/RoomId<br/>nctalks://user:pass@host/RoomId1/RoomId2/RoomIdN
| [Notica](https://github.com/caronc/apprise/wiki/Notify_notica) | notica://  | (TCP) 443   | notica://Token/
| [Notifico](https://github.com/caronc/apprise/wiki/Notify_notifico) | notifico://  | (TCP) 443   | notifico://ProjectID/MessageHook/
| [Office 365](https://github.com/caronc/apprise/wiki/Notify_office365) | o365://  | (TCP) 443   | o365://TenantID:AccountEmail/ClientID/ClientSecret<br />o365://TenantID:AccountEmail/ClientID/ClientSecret/TargetEmail<br />o365://TenantID:AccountEmail/ClientID/ClientSecret/TargetEmail1/TargetEmail2/TargetEmailN
| [OneSignal](https://github.com/caronc/apprise/wiki/Notify_onesignal) | onesignal:// | (TCP) 443 | onesignal://AppID@APIKey/PlayerID<br/>onesignal://TemplateID:AppID@APIKey/UserID<br/>onesignal://AppID@APIKey/#IncludeSegment<br/>onesignal://AppID@APIKey/Email
| [Opsgenie](https://github.com/caronc/apprise/wiki/Notify_opsgenie) | opsgenie:// | (TCP) 443 | opsgenie://APIKey<br/>opsgenie://APIKey/UserID<br/>opsgenie://APIKey/#Team<br/>opsgenie://APIKey/\*Schedule<br/>opsgenie://APIKey/^Escalation
| [ParsePlatform](https://github.com/caronc/apprise/wiki/Notify_parseplatform) | parsep:// or parseps:// | (TCP) 80 or 443 | parsep://AppID:MasterKey@Hostname<br/>parseps://AppID:MasterKey@Hostname
| [PopcornNotify](https://github.com/caronc/apprise/wiki/Notify_popcornnotify) | popcorn://  | (TCP) 443   | popcorn://ApiKey/ToPhoneNo<br/>popcorn://ApiKey/ToPhoneNo1/ToPhoneNo2/ToPhoneNoN/<br/>popcorn://ApiKey/ToEmail<br/>popcorn://ApiKey/ToEmail1/ToEmail2/ToEmailN/<br/>popcorn://ApiKey/ToPhoneNo1/ToEmail1/ToPhoneNoN/ToEmailN
| [Prowl](https://github.com/caronc/apprise/wiki/Notify_prowl) | prowl://   | (TCP) 443    | prowl://apikey<br />prowl://apikey/providerkey
| [PushBullet](https://github.com/caronc/apprise/wiki/Notify_pushbullet) | pbul://    | (TCP) 443    | pbul://accesstoken<br />pbul://accesstoken/#channel<br/>pbul://accesstoken/A_DEVICE_ID<br />pbul://accesstoken/email@address.com<br />pbul://accesstoken/#channel/#channel2/email@address.net/DEVICE
| [Pushjet](https://github.com/caronc/apprise/wiki/Notify_pushjet) | pjet:// or pjets:// | (TCP) 80 or 443 | pjet://hostname/secret<br />pjet://hostname:port/secret<br />pjets://secret@hostname/secret<br />pjets://hostname:port/secret
| [Push (Techulus)](https://github.com/caronc/apprise/wiki/Notify_techulus) | push://    | (TCP) 443    | push://apikey/
| [Pushed](https://github.com/caronc/apprise/wiki/Notify_pushed) | pushed://    | (TCP) 443    | pushed://appkey/appsecret/<br/>pushed://appkey/appsecret/#ChannelAlias<br/>pushed://appkey/appsecret/#ChannelAlias1/#ChannelAlias2/#ChannelAliasN<br/>pushed://appkey/appsecret/@UserPushedID<br/>pushed://appkey/appsecret/@UserPushedID1/@UserPushedID2/@UserPushedIDN
| [Pushover](https://github.com/caronc/apprise/wiki/Notify_pushover)  | pover://   | (TCP) 443   | pover://user@token<br />pover://user@token/DEVICE<br />pover://user@token/DEVICE1/DEVICE2/DEVICEN<br />**Note**: you must specify both your user_id and token
| [PushSafer](https://github.com/caronc/apprise/wiki/Notify_pushsafer)  | psafer:// or psafers://  | (TCP) 80 or 443  | psafer://privatekey<br />psafers://privatekey/DEVICE<br />psafer://privatekey/DEVICE1/DEVICE2/DEVICEN
| [Reddit](https://github.com/caronc/apprise/wiki/Notify_reddit) | reddit:// | (TCP) 443   | reddit://user:password@app_id/app_secret/subreddit<br />reddit://user:password@app_id/app_secret/sub1/sub2/subN
| [Rocket.Chat](https://github.com/caronc/apprise/wiki/Notify_rocketchat) | rocket:// or rockets://  | (TCP) 80 or 443   | rocket://user:password@hostname/RoomID/Channel<br />rockets://user:password@hostname:443/#Channel1/#Channel1/RoomID<br />rocket://user:password@hostname/#Channel<br />rocket://webhook@hostname<br />rockets://webhook@hostname/@User/#Channel
| [Ryver](https://github.com/caronc/apprise/wiki/Notify_ryver) | ryver://  | (TCP) 443   | ryver://Organization/Token<br />ryver://botname@Organization/Token
| [SendGrid](https://github.com/caronc/apprise/wiki/Notify_sendgrid) | sendgrid://  | (TCP) 443   | sendgrid://APIToken:FromEmail/<br />sendgrid://APIToken:FromEmail/ToEmail<br />sendgrid://APIToken:FromEmail/ToEmail1/ToEmail2/ToEmailN/
| [ServerChan](https://github.com/caronc/apprise/wiki/Notify_serverchan) | serverchan://   | (TCP) 443    | serverchan://token/
| [SimplePush](https://github.com/caronc/apprise/wiki/Notify_simplepush) | spush://   | (TCP) 443    | spush://apikey<br />spush://salt:password@apikey<br />spush://apikey?event=Apprise
| [Slack](https://github.com/caronc/apprise/wiki/Notify_slack) | slack://  | (TCP) 443   | slack://TokenA/TokenB/TokenC/<br />slack://TokenA/TokenB/TokenC/Channel<br />slack://botname@TokenA/TokenB/TokenC/Channel<br />slack://user@TokenA/TokenB/TokenC/Channel1/Channel2/ChannelN
| [SMTP2Go](https://github.com/caronc/apprise/wiki/Notify_smtp2go) | smtp2go:// | (TCP) 443 | smtp2go://user@hostname/apikey<br />smtp2go://user@hostname/apikey/email<br />smtp2go://user@hostname/apikey/email1/email2/emailN<br />smtp2go://user@hostname/apikey/?name="From%20User"
| [Streamlabs](https://github.com/caronc/apprise/wiki/Notify_streamlabs) | strmlabs:// | (TCP) 443 | strmlabs://AccessToken/<br/>strmlabs://AccessToken/?name=name&identifier=identifier&amount=0&currency=USD
| [SparkPost](https://github.com/caronc/apprise/wiki/Notify_sparkpost) | sparkpost:// | (TCP) 443 | sparkpost://user@hostname/apikey<br />sparkpost://user@hostname/apikey/email<br />sparkpost://user@hostname/apikey/email1/email2/emailN<br />sparkpost://user@hostname/apikey/?name="From%20User"
| [Spontit](https://github.com/caronc/apprise/wiki/Notify_spontit) | spontit://  | (TCP) 443   | spontit://UserID@APIKey/<br />spontit://UserID@APIKey/Channel<br />spontit://UserID@APIKey/Channel1/Channel2/ChannelN
| [Syslog](https://github.com/caronc/apprise/wiki/Notify_syslog) | syslog://  | (UDP) 514 (_if hostname specified_) | syslog://<br />syslog://Facility<br />syslog://hostname<br />syslog://hostname/Facility
| [Telegram](https://github.com/caronc/apprise/wiki/Notify_telegram) | tgram://  | (TCP) 443   | tgram://bottoken/ChatID<br />tgram://bottoken/ChatID1/ChatID2/ChatIDN
| [Twitter](https://github.com/caronc/apprise/wiki/Notify_twitter) | twitter://  | (TCP) 443   | twitter://CKey/CSecret/AKey/ASecret<br/>twitter://user@CKey/CSecret/AKey/ASecret<br/>twitter://CKey/CSecret/AKey/ASecret/User1/User2/User2<br/>twitter://CKey/CSecret/AKey/ASecret?mode=tweet
| [Twist](https://github.com/caronc/apprise/wiki/Notify_twist) | twist://  | (TCP) 443   | twist://password:login<br/>twist://password:login/#channel<br/>twist://password:login/#team:channel<br/>twist://password:login/#team:channel1/channel2/#team3:channel
| [XBMC](https://github.com/caronc/apprise/wiki/Notify_xbmc) | xbmc:// or xbmcs://    | (TCP) 8080 or 443   | xbmc://hostname<br />xbmc://user@hostname<br />xbmc://user:password@hostname:port
| [XMPP](https://github.com/caronc/apprise/wiki/Notify_xmpp) | xmpp:// or xmpps://    | (TCP) 5222 or 5223   | xmpp://user:password@hostname<br />xmpps://user:password@hostname:port?jid=user@hostname/resource<br/>xmpps://user:password@hostname/target@myhost, target2@myhost/resource
| [Webex Teams (Cisco)](https://github.com/caronc/apprise/wiki/Notify_wxteams) | wxteams://  | (TCP) 443   | wxteams://Token
| [Zulip Chat](https://github.com/caronc/apprise/wiki/Notify_zulip) | zulip://  | (TCP) 443   | zulip://botname@Organization/Token<br />zulip://botname@Organization/Token/Stream<br />zulip://botname@Organization/Token/Email

## Sending Notifications
There are two ways to send a notification, and both do the same thing: a `POST` method and a `GET` method.
You can see the Swagger documentation by adding `/docs` to the end of the URL.

[![Swagger documentation](https://raw.githubusercontent.com/t0mer/apprise-api-bridge/main/images/apprise%20api%20bridge%20-%20Swagger.png?raw=true)](https://raw.githubusercontent.com/t0mer/apprise-api-bridge/main/images/apprise%20api%20bridge%20-%20Swagger.png?raw=true)

**POST** (form fields; `group`, `title` and `message` are all required):
```bash
curl -X POST http://localhost:8080/api/notifications/push \
  -F group=admins \
  -F title="Backup finished" \
  -F message="Nightly backup completed successfully"
```

**GET** (query parameters):
```bash
curl -G http://localhost:8080/api/notifications/push \
  --data-urlencode group=admins \
  --data-urlencode title="Disk alert" \
  --data-urlencode message="Disk usage is above 90%"
```

## API Reference
Interactive documentation is served at `/docs` (Swagger UI) and `/redoc` (ReDoc); the OpenAPI schema is at `/openapi.json`.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Web UI (YAML configuration editor). |
| `GET` | `/api/config/load` | Returns the content of `config.yaml` as a string. |
| `POST` | `/api/config/save` | Overwrites `config.yaml`. JSON body: `{"configuration": "<YAML text>"}`. |
| `GET` | `/api/groups/get` | Returns the list of group names, e.g. `["admins"]`. **Currently broken:** returns HTTP 500 in the published image (see [Troubleshooting](#troubleshooting)). |
| `POST` | `/api/notifications/push` | Sends a notification. Form fields: `group`, `title`, `message` (all required). |
| `GET` | `/api/notifications/push` | Sends a notification. Query parameters: `group`, `title`, `message`. |
| `GET` | `/metrics` | Prometheus metrics (via `starlette-exporter`). |

Examples:

```bash
# List groups (currently returns HTTP 500 in the published image, see Troubleshooting)
curl http://localhost:8080/api/groups/get

# Download the current configuration
curl http://localhost:8080/api/config/load

# Replace the configuration
curl -X POST http://localhost:8080/api/config/save \
  -H "Content-Type: application/json" \
  -d '{"configuration": "admins:\n  - tgram://bottoken/ChatID\n"}'
```

Responses of the push and save endpoints are a JSON-encoded string that contains a JSON object:

```text
"{\"message\":\"Configuration updated\",\"success\":\"true\"}"
"{\"error\":\"Aw Snap! something went wrong ...\",\"success\":\"false\"}"
```

The push endpoints return the same `"Configuration updated"` message on success. `success` is `"false"` only when
the request itself fails (for example, an unknown group). It does not report whether each channel actually delivered
the message; check the container logs for Apprise delivery errors.

## Security Notes
* The API and the web UI have **no authentication**. Anyone who can reach port 8080 can send notifications, read
  `config.yaml` (which contains your tokens and passwords) and overwrite it.
* CORS allows all origins.
* Run the service on a trusted network only, or put it behind a reverse proxy that adds authentication and TLS.
* Treat `config.yaml` as a secret file.

## Troubleshooting
* **`"success":"false"` with an error such as `Aw Snap! something went wrong 'mygroup'`** – the requested group doesn't exist in `config.yaml`. Group names are case-sensitive.
* **A channel doesn't receive messages but the API reports success** – the response doesn't reflect per-channel
  delivery. Check `docker logs appriseapi` and verify the Apprise URL against the [Apprise wiki](https://github.com/caronc/apprise/wiki).
* **Configuration disappears after an update** – the configuration lives inside the container. Bind-mount
  `config.yaml` as shown in [Configuration](#configuration).
* **`/api/groups/get` returns HTTP 500** – the endpoint calls `yaml.load()` without a `Loader`. The published image
  (`techblog/apprise-api-bridge:1.0.1`) ships PyYAML 6.0, which requires a `Loader` argument, so the call raises a
  `TypeError` and the endpoint always fails. Read the group names from `/api/config/load` instead.

## Development
Project layout:

```text
app/
  app.py            # FastAPI application (all endpoints)
  config.yaml       # default groups file
  VERSION           # version shown in the UI and API docs
  templates/        # web UI (index.html)
  dist/             # static assets (Bootstrap, jQuery, Ace editor, select2)
images/             # README screenshots
Dockerfile          # based on techblog/fastapi, adds apprise and PyYAML
.github/workflows/  # image publishing (Docker Hub, JFrog; GHCR workflow unused)
```

Run from source (the app uses relative paths, so start it from the `app/` directory):

```bash
pip install fastapi uvicorn apprise pyyaml pyaml loguru jinja2 aiofiles requests python-multipart starlette-exporter
cd app
python app.py
```
<!-- TODO: verify the full dependency list; the Docker image gets most of it from the techblog/fastapi base image -->

The service is then available at `http://localhost:8080`.

Docker images are built by GitHub Actions:
* `docker-image.yml` – on a published GitHub release, pushes `techblog/apprise-api-bridge:latest` and
  `:<app/VERSION>` for `linux/amd64`, `linux/arm64` and `linux/arm/v7`.
* `publish-ghcr.yml` – manual workflow for `ghcr.io/t0mer/apprise-api-bridge`; it has not been run, so nothing is published to GHCR yet.
* `jcr-image.yml` – manual run, pushes to a private JFrog registry.

## Contributing
Issues and pull requests are welcome at [github.com/t0mer/apprise-api-bridge](https://github.com/t0mer/apprise-api-bridge).

## License
This project is licensed under the Apache License 2.0. See the [License](License) file for details.
