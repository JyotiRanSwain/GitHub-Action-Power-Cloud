#Base image
FROM tomcat:8.5

#COPY
COPY $GITHUB_WORKSPACE/web/target/time-tracker-web-0.5.0-SNAPSHOT.war /usr/local/tomcat/webapps/

WORKDIR /usr/local/tomcat/webapps/

CMD ["catalina.sh", "run"]
