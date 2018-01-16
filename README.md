# Cucumber-cats (Azure version)

THis is a variant of the cucumber_cats branch for automatic deployment through
Azure Web Apps.

Some information on the work done in this branch can be found on this private repo:

https://github.com/UCL-RITS/CloudLabs/wiki/Hello-Flask-Docker-Azure

Here's a summary:

I've created a simple app in Flask that displays random pictures of cats being scared by cucumbers, because reasons.

__Requirements__:

* Python
  * I created a virtual env with: `mkvirtualenv -p python3 cloudlabs`
* Flask (latest is 0.12.1)

__The app's code is here__:

 ```python
from flask import Flask, render_template
import random

app = Flask(__name__)

# list of cat images
images = [
    "http://i.imgur.com/MljgJNN.gif",
    "http://i.imgur.com/s7Muc32.gif",
    "https://media0.giphy.com/media/CNf1SeN6fcBuo/giphy.gif",
    "https://media4.giphy.com/media/N5eUbQfWEzLqg/giphy.gif",
    "https://media0.giphy.com/media/DwtfcPtkcnCtq/giphy.gif"
]

@app.route('/')
def index():
    url = random.choice(images)
    return render_template('index.html', url=url)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
```

`index.html` is in the templates folder in the repo https://github.com/UCL-RITS/CloudLabs/tree/hello-flask-docker-azure/hello-flask-cucumber-cats

Run as:

```
export FLASK_APP=~/workspace/cucumber-cat/app.py
flask run
```

## Dockerized Flask app
Azure is supposed to work well with Docker containers, and CloudLabs will be based on Docker for its initial prototype, so I tried to run my flask app on a Docker container.

__Requirements__:
* Docker for Mac
 * I'm using version 17.03.1-ce-mac12 (17661)

__Dockerfile__:

```
# our base image
FROM alpine:3.5

# Install python and pip
RUN apk add --update py2-pip

# install Python modules needed by the Python app
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

# copy files required for the app to run
COPY app.py /usr/src/app/
COPY templates/index.html /usr/src/app/templates/

# tell the port number the container should expose
EXPOSE 5000

# Useful if Flask 0.12 is ever going to work with Docker
ENV FLASK_APP /usr/src/app/app.py

# run the application
CMD ["python", "/usr/src/app/app.py"]
```

Note version 0.12 of Flask (latest available) will let you run this applications with `flask run` after exporting the `FLASK_APP` env variable and make it point to `app.py`. However this doesn't work with Docker, so I had to run it as `python app.py`.

__Run__:

```
docker build -t hello-flask .
docker run -p 5000:5000 hello-flask
```

Then curl/browse: `localhost:5000` and reload for random images of cats getting scared of cucumbers.

## Docker-compose
For now we only have one Flask app, but we might want to make it talk to other services like data stores. I've also seen everywhere that Flask apps (and other python web apps) are normally run with Apache or Nginx, so we might need to have a container for each of these. In order to make those containers talk to each other and be deployed as a scalable stack, we can user `docker-compose`.

__Configure__:
For this I added a `docker-compose.yml` file:

```
version: "3"
services:
  cat-cucumber:
    build: .
    ports:
      - "5000:5000"
```

Version 3 is the latest version of docker-compose yaml.

For now, we only have one service: __cat-cucumber__.

This service can be built using the Dockerfile in the current folder `.`, and running mapping port `5000` to host's `5000`.

__Run__:

```
docker-compose up
```

And access/curl `localhost:5000`.


## Docker Swarm
Azure Containers are optimised container solutions on the cloud. They are designed for clusters, but they are the only container solution Azure provides other than creating a VM and manually installing docker there. So in order to test the cucumber cats web app on Azure, I need to make it work in Docker Swarm locally first.

To enter the Docker-Swarm mode:

```
docker swarm init
```

This creates a swarm with a single node, which is the swarm master. Docker Swarm has evolved from Docker compose, so the compose yaml file used in the previous section can also be used here. However, the compose config files accepted by swarm are a subset of the ones accepted by docker-compose, and they won't accept things like "build". They require images. Local images are also not enough, so I had to build the images and push it to my docker repository in

https://hub.docker.com/r/zapatilla/hello-cucumber/

I did this like this:

```
docker login
docker build ...
docker tag ...
docker push ...
```

So now my `docker-compose.yml` file looks like this:

```yaml
version: "3"
services:
  cat-cucumber:
    image: zapatilla/hello-cucumber
    ports:
      - "5000:5000"
```

To run it in the swarm:

```
docker deploy -c docker-compose.yml hello-swarm
```

To see the services deployed:

```
docker service ls
```

Kill it with:

```
docker service rm hello-swarm_cat-cucumber
```

Leave the swarm with:

```
docker swarm leave [--force]
```

Now we should be ready to do this on Azure!


## Azure Containers via Azure Portal

1. Go to the Azure portal https://portal.azure.com
1. Select __New__ -> Type __ACS__ on the search field -> Choose `Azure Container Service`
1. Configure accepting defaults and choosing Swarm as orchestrator. You'll need a SSH key with u+rw permission __only__. Others and all should have 0 permissions on the key (Azure won't allow ssh-ing otherwise, and you __must__ have a non empty passphrase!).
1. I use DS1 for tests since it's cheaper.
1. Sit back and relax - deployment takes 15-20 minutes!!
1. Once it's ready, find IP for the Swarm master by going to the resource group and finding the master, then navigate to its settings.
1. SSH to that IP. Note that for ACS (not for the other VMs) you'll need to pass the -i switch, even if you have a nicely configured ssh config file. Otherwise you enter your passphrase and it claims it's wrong all the time. So do:
  ``` ssh -i ~/.ssh/id_rsa_azure  raquel@13.94.250.239```
1. Copy there your `docker-compose.yml` and whatever other files needed for the cucumber cats web app. Git clone?
1. `cd` to relevant directory and run `docker deploy -c docker-compose.yml hello-swarm`.
1. Access from outside on IP:5000. Perhaps inbound rules needed?

Right, of course it doesn't work:

* Docker deploy is not supported
 ```
$ docker deploy -c docker-compose.yml hello-swarm
docker deploy is only supported on a Docker daemon with experimental features enabled
```

* Docker compose is supported, but only version 2, whilst my docker-compose.yml file uses version 3.
 ```
$ docker-compose up
ERROR: Version in "./docker-compose.yml" is unsupported. Either specify a version of "2" (or "2.0") and place your service definitions under the `services` key, or omit the `version` key and place your service definitions at the root of the file to use version 1.
For more on the Compose file format versions, see https://docs.docker.com/compose/compose-file/
```

* So you need to build and run:
 ```
docker build -t hello-flask .
docker run -p 5000:5000 hello-flask
```

* Now you can access from within the machine with
 ```
curl localhost:5000
```

* To access from the outside, you have to change the load balancer inbound rules. For that:
  1. Go to portal.azure.com and find the resource group you created for the container service
  1. One of the things in the list will be a Load Balancer which looks like `XYZ-agent-lb-XYZ`. Click on it.
  1. Select "Health Probes". So intuitive... You'll see the default open ports: 80, 443, 8080.
  1. You can make your docker container expose 5000 on 8080, or [open the 5000 end point in the load balancer](https://docs.microsoft.com/en-us/azure/container-service/container-service-enable-public-access). However none of those worked for me... I give up. I might try with other orchestrators some other time.
