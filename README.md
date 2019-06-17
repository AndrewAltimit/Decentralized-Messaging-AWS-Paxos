# Overview
A decentralized, fault-tolerant, messaging service on AWS using CloudFormation / EC2. By combining the Paxos algorithm with AWS's infrastructure - we were able to create a service that can reach consensus, withstand failures of an availability zone (nodes spread over 3 AZs by default), and recover from data loss and other disasters.


## Contributors

<a href="https://github.com/AndrewAltimit/Decentralized-Messaging-AWS-Paxos/graphs/contributors">
  <img src="contributors.png" />
</a>


## AWS Services
* CloudFormation
* Elastic Compute Cloud (EC2)


## AWS Deployment using CloudFormation

###### Inside the "AWS Deployment" folder you'll find the CloudFormation template used in the deployment below

1. Create a new stack in CloudFormation and upload **template.json**.


2. Specify the stack name, private IPs (ensure subnet exists in that AZ), usernames, EC2 Key Pair, and the range of IPs you'd like to have SSH access to your cluster. 

    Default settings provided will deploy in us-west-2a, us-west-2b, us-west-2c using Amazon Linux 2 ami's and give SSH access to all IPs. 
    
    **It is highly recommended you restrict SSH access to only your public IP**, such as 163.162.122.3.55/32 where 163.162.122.3.55 is the public IP of the remote user.


## Usage

Once deployed, you are able to launch the user interface where you can tweet messages, view timeline, follow/unfollow users, view logs, etc. This interface can be launched from within the cluster or locally on your own machine.

****Messaging within the Cluster****

1. SSH to one of the EC2 public IPs using the same Key Pair specified in step 2
2. Run the following to switch the server to interactive mode and initiate the messaging client:

       cd /twitter/src/
       sudo sh run_client.sh
    


****Messaging Remotely over Internet****

1. Download a copy of the git repository
2. Update **server_hosts.txt** to include the public IP addresses of your EC2 instances:

       EC2_PUBLIC_IP 9021 9022 9023
       EC2_PUBLIC_IP 9021 9022 9023
       EC2_PUBLIC_IP 9021 9022 9023

3. Navigate to the src directory and launch message.py to initiate the messaging client.

Ensure that your machine has ports 9021-9023 open as these are the ports the servers will attempt to communicate to you on.

