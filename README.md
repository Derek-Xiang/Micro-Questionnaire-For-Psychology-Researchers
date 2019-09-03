Micro Questionnaire For Psychology Researchers(Flask+Mysql+AWS ec2/s3+nginx)

This is a small web application which allows participants to register and login securely, and finish their questions in one week, whose data will be stored in mysql database. <br>
DATABASE:
  --research
    --comments
    --colours
    --users

The app is deployed on a ec2 machine on aws by nginx engine to deploy its production environment and because of high availability of data, the database is backup-ed with s3 every 24 hours. (not required high throughput, so LB or ASG are not used)
