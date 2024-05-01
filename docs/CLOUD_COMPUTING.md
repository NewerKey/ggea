<div align="center">
<h3>Cloud Operations for GGEA Backend API</h3>
<h3>Department of Software Engineering </h3>
<h3> SE_09 Cloud Computing </h3>
<h3>Spring Semester 2023</h3>
<h3>Adam Roe</h3>
<h3>April 28, 2023 </h3>
</div>

### Team Members
- Yvette Nuerkie Nartey
- Josef Leinweber

# Architecture

### Cloud Infrastructure (Logical Design) 🏗️

![GGEA Image](https://github.com/Aeternalis-Ingenium/GGEA/blob/trunk/docs/images/GGEA_Cloud%20Infrastructure.jpeg)

- [Lucid Chart Share Link](https://lucid.app/lucidchart/invitations/accept/inv_eb7c3f72-06c1-4d4c-a747-282782f436e9)

# Billing

### Create an GCP Budget
We set a budget(preferably within free tier range) and created a notification alert for when it is reached. 

# Security Considerations 🔐

### IAM_User Management
We created a new user and gave it some admin roles to be able to access just our project and its resources.This is best practice not to use our root user for deployment.   
[IAM User Management](https://console.cloud.google.com/iam-admin/serviceaccounts?project=symmetric-stage-317508).

### Set Env Vars

We set environment variables and stored them in the secret manager service. 

# Project in production 🚀

Deployed application: [link](https://ggea-with-ssl-db-connection-rgmw4e5pva-od.a.run.app/redoc)
