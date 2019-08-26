node {
  // Mark the code checkout 'stage'....
    
   
stage ('Stage Checkout'){

  // Checkout code from repository and update any submodule
    
    
  checkout scm
    
  } 
 // sh 'git submodule update --init'  

  //stage 'Stage Build'
  
  stage('build') {
            
                echo 'Building..'
                
                sh "./spoken.sh"
              
                
            
        } 
    
   stage('test')
     {
      sh "./tests.sh"  
//      sh "./selen.sh"
     }
   
  stage('deploy')
     {
      sh "./deploy.sh"   
       }  
  
  //branch name from Jenkins environment variables
  // echo "My branch is: ${env.BRANCH_NAME}"

//  def flavor = flavor(env.BRANCH_NAME)
 // echo "Building flavor ${flavor}"

  //build your gradle flavor, passes the current build number as a parameter to gradle
//  sh "./gradlew clean assemble${flavor}Debug -PBUILD_NUMBER=${env.BUILD_NUMBER}"

//  stage 'Stage Archive'
  //tell Jenkins to archive the apks
//  archiveArtifacts artifacts: 'app/build/outputs/apk/*.apk', fingerprint: true

//  stage 'Stage Upload To Fabric'
 // sh "./gradlew crashlyticsUploadDistribution${flavor}Debug  -PBUILD_NUMBER=${env.BUILD_NUMBER}"
  
}
