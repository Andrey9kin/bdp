Better CI results visualization with Jenkins, Dashing and Groovy black magic
############################################################################

:date: 2013-09-29 06:00
:tags: ci, jenkins, dashing, radiator, getting started, example, data visualization, groovy, cd, automation
:category: Tools
:slug: getting-started-with-dashing
:author: Andrey Devyatkin
:summary: Example of how you can visualize data from Jenkins using Dashing framework

Intro
-----

Jenkins is a great and powerful automation tool. It has a lot of plugins that makes it a good fit for more or less every task. But when it comes to your build/test/release flow presentations as well as showing statistics then things are not that shiny. All walldisplay/radiator plugins available today are too general and designed by engineers for engineers. Most famous plugins are `Walldisplay <https://wiki.jenkins-ci.org/display/JENKINS/Wall+Display+Plugin>`_

.. image::  ../../static/images/walldisplay.png
   :align:  center

and `eXtreme Feedback Panel <https://wiki.jenkins-ci.org/display/JENKINS/eXtreme+Feedback+Panel+Plugin>`_

.. image::  ../../static/images/extremefeedback.png
   :align:   center

As you can see both of them designed to track build and test progress but if you want to display something more than that then you have a problem. Of course, it is possible to create and configure Jenkins views and there you can go quite far. But it would be much better to have something out-of-the-box, or at least templates, prepared by people who knows how to do graphical design. So we are looking for something that is configurable, extensible and looks good out-of-the-box. And at this moment `Dashing <http://shopify.github.io/dashing/>`_ enters scene.

Dashing
-------

According to the main page Dashing is - the exceptionally handsome dashboard framework. Well, that is all I need.  Let’s check details. Basically Dashing is a visualization platform, i.e. it provides you with widgets, built in web server to serve them, REST HTTP interface to feel them with data. It means that we only need to configure what widgets to use, how they look like and start to push data there. And that is it.

Installation and configuration
++++++++++++++++++++++++++++++

I see no point to copy installation instructions to here so please refer to the Dashing page and follow `installation instructions <http://shopify.github.io/dashing/#setup>`_.
Now I assume that you have Dashing installed. Time to create example project::

    dashing new example
    cd example
    bundle
    dashing start

At this stage I got this right in to my face::

    gems/execjs-2.0.1/lib/execjs/runtimes.rb:51:in `autodetect': Could not find a JavaScript runtime. See https://github.com/sstephenson/execjs for a list of available runtimes. (ExecJS::RuntimeUnavailable)

No JavaScript runtime. That is fixable. Add *gem ‘execjs’* and *gem ‘therubyracer’* to  Gemfile and try again::

    bundle
    dashing start

And now web server started::

    >> Thin web server (v1.5.1 codename Straight Razor)
    >> Maximum connections set to 1024
    >> Listening on 0.0.0.0:3030, CTRL+C to stop
    For the twitter widget to work, you need to put in your twitter API keys in the jobs/twitter.rb file.
    127.0.0.1 - - [10/Sep/2013 21:11:37] "GET /sample HTTP/1.1" 200 2276 0.0091

Open localhost:3030 in a browser to check out sample project provided together with Dashing

.. image::  ../../static/images/firstrun.png
   :align:  center

Looks great, isn’t? Now it is a right time to take a pause and think about what will can show there.

Nowadays people mostly ask me few questions:

- How fast out CI builds are?
- How many changes we delivered today?
- How many test cases we are executing in our CI checks?  

Let's see how we can use existing widgets to show this info:

- widget Graph (Convergence). Looks like a good fit for a build time trend for CI build/test job so developers can estimate how fast they will get a feedback. That is also important for me to be able to monitor and catch situation when build time trend is going up. If we catch it early enough then we can investigate reasons and try to prevent it in the future
- widget List (Buzzwords). Quite often testing of submitted changes is distributed between multiple jobs running in parallel and it is quite hard to get good overview of all executed test cases. So in this widget we will place info about latest submitted commit status.
- widget Number (Current Valuation). What to place there? Number of changes submitted today. Would be fun to see how productive our developers today. Value of this info is the same as value of build time trend – if you see that number is constantly growing then time to order some more build machines. 
- widget Text (Hello). That will be a place from where we will speak with the world. There you can place different kind of information that you are normally sending via mail. Let say somebody really talented managed somehow bring build fault through build check to development branch. You can then post this info there in order to notify everybody that development branch is broken and they need to concentrate on fixing it instead of pushing new changes in. But this is quite rare occasion. For the other time you can use it for a something else. For example to say happy birthday to your colleagues.
- widget Meter (Synergy). I have no good idea for this one, so just removed it

All those widgets and their location described in *dashboards/sample.erb*. Let’s remove Meter widget from there and rename other widgets in order to have descriptive and meaningful interfaces. I changed that in this way::

    <% content_for :title do %>Example<% end %>
    <div class="gridster">
      <ul>
	<li data-row="1" data-col="1" data-sizex="2" data-sizey="1">
  	  <div data-id="test-status" data-view="List" data-unordered="true" data-title="Latest commit status"></div>
	</li>
	<li data-row="1" data-col="1" data-sizex="2" data-sizey="1">
          <div data-id="information" data-view="Text" data-title="Information board" data-text=""></div>
	</li>
	<li data-row="1" data-col="1" data-sizex="1" data-sizey="1">
  	  <div data-id="number-of-changes" data-view="Number" data-title="Number of commits submitted today"></div>
	</li>
	<li data-row="1" data-col="1" data-sizex="3" data-sizey="1">
  	  <div data-id="build-time-trend" data-view="Graph" data-title="Build time trend" style="background-color:#ff9618"></div>
	</li>
      </ul>
    </div>

and result

.. image::  ../../static/images/secondrun.png
   :align:  center

It looks less fancy without data but we just about to fix that.

Jenkins
-------

There are two ways to get data out from Jenkins. Push and pull, i.e. you can use Jenkins HTTP interface to pull data by setting Dashing jobs, or you can collect data inside Jenkins using groovy scripts or regular jobs and then push data to Dashing over HTTP. This is up to you decide how to do that. I decided to go second way because I was looking for opportunity to play with Groovy scripting inside Jenkins and can recall former colleague of me, who wrote one of the previous walldisplays using Jenkins interface to pull data from it. If be correct I recall all those swearing’s he used during writing.
What data we can get with Groovy? We are about to manipulate with Jenkins internal data structures and it means any data.

Build time trend
++++++++++++++++

Let’s prepare Groovy script that will collect this info. First we need to get object representing a job, we are interested in, and then traverse latest, let’s say, 100 builds. Open “Script Console”, i.e. *Manage Jenkins -> Script Console* in your sandbox Jenkins (Always test scripts in a sandbox instance before run them in production!) and then run script below (Please don't judge strictly - I'm quite new to Groovy and that's why is a bit python'ish). Don’t forget to replace “some job name” with a real job name::

  String jobName = "some job name"
  def jsonBuilder = new groovy.json.JsonBuilder()
  def job = jenkins.model.Jenkins.instance.getItem(jobName)
  // Check that job exists
  if ( ! job ) {
    println "No job with name " + jobName + " found"
    return
  }
  int buildNumber = 0
  String out = ""
  for (build in job.getBuilds()) {
    // Skip ongoing build
    if ( ! build.result ) { continue }
    if ( build.result == Result.SUCCESS ) {
      // Ugly hack to get coma separated list
      if (buildNumber != 0) { out += ',' }
      // Generate json fragment
      jsonBuilder(x: buildNumber, y: build.getDurationString().split()[0])
      // Add fragment to resulting string
      out += jsonBuilder.toString()
      buildNumber++
      if (buildNumber > 100) { break }
    }
  }
  println out

It should get something like this::

    {"x":0,"y":"21"},{"x":1,"y":"21"},{"x":2,"y":"20"},{"x":3,"y":"21"},{"x":4,"y":"22"},{"x":5,"y":"20"},{"x":6,"y":"22"},{"x":7,"y":"21"},{"x":8,"y":"23"},{"x":9,"y":"22"},{"x":10,"y":"23"},{"x":11,"y":"21"},{"x":12,"y":"21"},{"x":13,"y":"21"},{"x":14,"y":"21"},{"x":15,"y":"21"},{"x":16,"y":"22"},{"x":17,"y":"23"},{"x":18,"y":"21"},{"x":19,"y":"21"},{"x":20,"y":"31"},{"x":21,"y":"27"},{"x":22,"y":"22"},{"x":23,"y":"21"},{"x":24,"y":"21"},{"x":25,"y":"21"},{"x":26,"y":"22"},{"x":27,"y":"21"},{"x":28,"y":"30"},{"x":29,"y":"27"},{"x":30,"y":"22"},{"x":31,"y":"21"},{"x":32,"y":"20"},{"x":33,"y":"20"},{"x":34,"y":"21"},{"x":35,"y":"25"},{"x":36,"y":"21"},{"x":37,"y":"20"},{"x":38,"y":"21"},{"x":39,"y":"23"},{"x":40,"y":"20"},{"x":41,"y":"21"},{"x":42,"y":"24"},{"x":43,"y":"24"},{"x":44,"y":"22"},{"x":45,"y":"21"},{"x":46,"y":"21"},{"x":47,"y":"26"},{"x":48,"y":"21"},{"x":49,"y":"21"},{"x":50,"y":"21"},{"x":51,"y":"21"},{"x":52,"y":"22"},{"x":53,"y":"25"},{"x":54,"y":"29"},{"x":55,"y":"32"},{"x":56,"y":"34"},{"x":57,"y":"24"},{"x":58,"y":"21"},{"x":59,"y":"25"},{"x":60,"y":"21"},{"x":61,"y":"21"},{"x":62,"y":"22"},{"x":63,"y":"24"},{"x":64,"y":"20"},{"x":65,"y":"21"},{"x":66,"y":"21"},{"x":67,"y":"23"},{"x":68,"y":"21"},{"x":69,"y":"23"},{"x":70,"y":"20"},{"x":71,"y":"21"},{"x":72,"y":"21"},{"x":73,"y":"21"},{"x":74,"y":"22"},{"x":75,"y":"21"},{"x":76,"y":"22"}

Last step is to send this info to graph widget::

  import org.apache.commons.httpclient.*
  import org.apache.commons.httpclient.methods.*
  import org.apache.commons.httpclient.methods.RequestEntity
  import org.apache.commons.httpclient.methods.StringRequestEntity
  import jenkins.*
  import jenkins.model.*
  import hudson.*
  import hudson.model.*

  String jobName = "some job name"
  String address = "http://localhost:3030/widgets/build-time-trend"

  def jsonBuilder = new groovy.json.JsonBuilder()
  def job = jenkins.model.Jenkins.instance.getItem(jobName)
  // Check that job exists
  if ( ! job ) {
    println "No job with name " + jobName + " found"
    return
  }
  int buildNumber = 0
  String out = ""
  for (build in job.getBuilds()) {
    // Skip ongoing build
    if ( ! build.result ) { continue }
    if ( build.result == Result.SUCCESS ) {
      // Ugly hack to get coma separated list
      if (buildNumber != 0) { out += ',' }
      // Generate json fragment. Important to provide integers, otherwise you will get very weird result!
      jsonBuilder(x: buildNumber.toInteger(), y: build.getDurationString().split()[0].toInteger())
      // Add fragment to resulting string
      out += jsonBuilder.toString()
      buildNumber++
      if (buildNumber > 100) { break }
    }
  }

  if ( out == "" ) {
    println "Nothing found"
    return
  }

  // Prepare HTTP request
  client = new HttpClient()
  post = new PostMethod(address)
  data = new StringRequestEntity('{"auth_token": "YOUR_AUTH_TOKEN", "points": [' + out + ']}')
  post.setRequestEntity(data)

  // Send data
  try {
    status = client.executeMethod( post );
    println status + "\n"
    println post.getResponseBody()
  } finally {
    post.releaseConnection();
  }

Please note that I added few imports. *hudson.** and *jenkins.** imports are not necessary in script console. But you have to have them if you are using `Groovy plugin <https://wiki.jenkins-ci.org/display/JENKINS/Groovy+plugin>`_ or `Scriptler plugin <https://wiki.jenkins-ci.org/display/JENKINS/Scriptler+Plugin>`_. I will write few lines about those plugings in the end. Now switch to dashing monitor to check build results

.. image::  ../../static/images/first-build-time-trend.png
   :align:  center

But wait a sec! What does 3K means and why we have seconds downthere? Both dimensions defined by default widget configuration and it is time to change that. All widgets are stored in widgets directory and described by 3 files. .scss - for style definition, .html - base page layout, .coffee - data rendering. We about to update *widgets/graph/graph.coffee*. Replace those lines::

  @graph.series[0].data = @get('points') if @get('points')
  x_axis = new Rickshaw.Graph.Axis.Time(graph: @graph)
  y_axis = new Rickshaw.Graph.Axis.Y(graph: @graph, tickFormat: Rickshaw.Fixtures.Number.formatKMBT)

with::

  Rickshaw.Fixtures.Number.Minutes =  (y) ->
    return y + ' min';
  @graph.series[0].data = @get('points') if @get('points')
  y_axis = new Rickshaw.Graph.Axis.Y(graph: @graph, tickFormat: Rickshaw.Fixtures.Number.Minutes)

and refresh a page

.. image::  ../../static/images/dashing-build-time-trend-fixed.png
   :align:  center


Deliveries counter
++++++++++++++++++

In my case I have Jenkins job that is triggered every time when new commit submitted to central repository. Assuming this I can count number of commits as number of builds executed for this job::

  import org.apache.commons.httpclient.*
  import org.apache.commons.httpclient.methods.*
  import org.apache.commons.httpclient.methods.RequestEntity
  import org.apache.commons.httpclient.methods.StringRequestEntity
  import jenkins.*
  import jenkins.model.*
  import hudson.*
  import hudson.model.*

  String jobName = "some job name"
  String address = "http://localhost:3030/widgets/number-of-changes"
  def job = jenkins.model.Jenkins.instance.getItem(jobName)
  // Check that job exists
  if ( ! job ) {
    println "No job with name " + jobName + " found"
    return
  }

  // Get today's date to be able to reset a counter
  def d = new Date()
  def today = d.format('yyyy-MM-dd', TimeZone.getTimeZone('GMT'))

  int counter = 0
  job.getBuilds().each {
  if ( it.result == Result.SUCCESS ) {
    buildDate = it.getTimestampString2().split('T')[0]
    if ( buildDate == today ) { counter++ }
    } 
  }

  // Prepare HTTP request
  client = new HttpClient()
  post = new PostMethod(address)
  data = new StringRequestEntity('{"auth_token": "YOUR_AUTH_TOKEN", "current": ' + counter + '}')
  post.setRequestEntity(data)

  // Send data
  try {
    status = client.executeMethod( post );
    println status + "\n"
    println post.getResponseBody()
  } finally {
    post.releaseConnection();
  }

Result

.. image::  ../../static/images/dashing-commits-counter.png
   :align:  center

Testing summary
+++++++++++++++

The biggest issue when aggregating downstream builds result is identification of the builds triggered by current build, i.e. there is no good way (as far as I know) how to identify them using Jenkins model methods. To workaround this issue you can define some parameter or environment variable and then pass it to downstream builds as parameter. Then you will use this parameter value as identifier. In my case job is triggered by `Gerrit trigger <https://wiki.jenkins-ci.org/display/JENKINS/Gerrit+Trigger>`_ and I'm using Gerrit variables as source of information and identifier::

  import org.apache.commons.httpclient.*
  import org.apache.commons.httpclient.methods.*
  import org.apache.commons.httpclient.methods.RequestEntity
  import org.apache.commons.httpclient.methods.StringRequestEntity
  import jenkins.*
  import jenkins.model.*
  import hudson.*
  import hudson.model.*

  // Function to look up downstream build and extract test results from it
  def getTestResultByEventId(jobName, id, eventId) {
    project = jenkins.model.Jenkins.instance.getItem(jobName)
    for (b in project.builds) {
      buildEnv = b.getEnvironment()
      if ( buildEnv[id] == eventId ) {
        println "Found " + b
        result = b.getTestResultAction()
        if ( result ) {
          notPassed = result.getFailCount() + result.getSkipCount()
          return result.getTotalCount() - notPassed + '/' + result.getTotalCount() + ' passed'
        } else { return 'No info found'} 
      }
    }
  }

  String jobName = "some job name"
  String address = "http://localhost:3030/widgets/test-status"
  def jsonBuilder = new groovy.json.JsonBuilder()
  def job = jenkins.model.Jenkins.instance.getItem(jobName)
  // Check that job exists
  if ( ! job ) {
    println "No job with name " + jobName + " found"
    return
  }

  // It could be that we are interested in not every downstream job
  // so I'm using list to specify jobs to check
  def downstream = ["downstream-test-job1", "downstream-test-job2"]
  // I'm using this variable value to identify downstream builds
  String id = "GERRIT_EVENT_HASH"
  String out = ""
  def build

  // Get latest completed build
  for (b in job.getBuilds()) {
    if ( b.state == Run.State.COMPLETED ) {
      println "Last completed build is " + b
      build = b
      break
    }
  }

  out = '{"label": "Committer", "value": "' + build.buildVariables.get('GERRIT_CHANGE_OWNER_NAME') + '"},'
  message = build.buildVariables.get('GERRIT_CHANGE_SUBJECT') 
  out += '{"label": "Commit msg", "value": "'
  if (message.size() > 35) {
    out +=  message.substring(0,34) + '..."}, '
  } else {
    out +=  message + '"}, '
  }

  String eventId = build.buildVariables.get(id)
  println id + " " + eventId
  for ( downstreamJob in downstream ) {
    println "Look for test results from " + downstreamJob
    out += '{"label": "' + downstreamJob + '", '
    out += '"value": "' + getTestResultByEventId(downstreamJob, id, eventId) + '"},'
  }

  // Prepare HTTP request
  client = new HttpClient()
  post = new PostMethod(address)
  // out[0..-2] needed to remove coma in the end
  data = new StringRequestEntity('{"auth_token": "YOUR_AUTH_TOKEN", "unordered": "true", "items": [' + out[0..-2] + ']}')
  post.setRequestEntity(data)

  // Send HTTP request
  try {
    status = client.executeMethod( post );
    println status + "\n"
    println post.getResponseBody()
  } finally {
    post.releaseConnection();
  }

result

.. image::  ../../static/images/dashing-test-results.png
   :align:  center

Information field
+++++++++++++++++

Last and easiest piece of work is information field update. We don't even need Groovy and Jenkins for this. Instead we will use our old friend *curl*::

  curl -d '{ "auth_token": "YOUR_AUTH_TOKEN", "text": "Wake up Neo..." }' http://localhost:3030/widgets/information

result

.. image::  ../../static/images/dashing-information.png
   :align:  center

Final automation
----------------

Remaining step is to automate those scripts execution. I strongly recommend you to use `Scriptler plugin <https://wiki.jenkins-ci.org/display/JENKINS/Scriptler+Plugin>`_ mentioned before. This plugin allows you to version control your scripts, execute them as build step and control execution privileges. Moreover this plugin allows you to share your scripts with community and re-use scripts from other developers.

That is it for this article. Happy hacking!  
