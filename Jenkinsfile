pipeline {
  agent any
  stages {
    stage('Build and Test') {
      steps {
        sh 'docker-compose build --no-cache'
        sh 'rm -f output.html'
        sh 'touch output.html'
        sh 'docker run -v $(pwd)/output.html:/usr/src/app/output.html houseofmisfits/aspen:latest debug'
      }
    }
    stage('Deploy Integration'){
      when {
        expression { BRANCH_NAME == 'integration' }
      }
      environment {
        WEBHOOKS_FILE = credentials('9adeeae1-50f8-4f8c-afac-b18df7d8b031')
      }
      steps {
        sh 'rm -rf webhooks.yml'
        sh 'cp $WEBHOOKS_FILE webhooks.yml'
        sh 'docker-compose down'
        sh 'docker-compose up -d'
      }
    }
    stage('Deploy Master'){
      when {
        expression { BRANCH_NAME == 'master' }
      }
      environment {
        WEBHOOKS_FILE = credentials('20c14f11-b6b2-441b-93e9-4bdcf8795eb1')
      }
      steps {
        sh 'rm -rf webhooks.yml'
        sh 'cp $WEBHOOKS_FILE webhooks.yml'
        sh 'docker-compose down'
        sh 'docker-compose up -d'
      }
    }
  }
  post {
    success {
      script {
        if (env.CHANGE_ID) {
          archiveArtifacts artifacts: 'output.html'
          pullRequest.comment("Output.html uploaded to ${env.BUILD_URL}artifact/output.html")
        }
      }
    }
  }
}
