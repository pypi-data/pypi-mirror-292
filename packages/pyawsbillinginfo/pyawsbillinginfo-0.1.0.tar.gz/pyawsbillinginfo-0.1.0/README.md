# pyawsbillinginfo
A CLI for getting AWS Billing information. To use this program create an IAM
user called pybilling.

![pybilling](https://jdrumgoole.s3.eu-west-1.amazonaws.com/aws_pybilling_user.png)


Now create a group called `pybilling_group` and attach the `AWSBillingConductorReadOnlyAccess` policy to the group:

![group](https://jdrumgoole.s3.eu-west-1.amazonaws.com/aws_pybilling_group.png)

Now add the `pybilling` user to the `pybilling` group:

![user group](https://jdrumgoole.s3.eu-west-1.amazonaws.com/aws_pybilling_group_member.png)

Now on the `pybilling` user page create a new access key and secret key:

![access key](https://jdrumgoole.s3.eu-west-1.amazonaws.com/create_access_key.png)

Once this is down you should install the `aws cli` from 
the [installer page](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

Once this is installed run `aws configure` and enter the access key and secret key you created above.

Now you can install the `pyawsbillinginfo` program by running:

```bash
pip install pyawsbillinginfo
```

Once this is done you can run the `pyawsbillinginfo` program. Use -h to get the options. 

If you are stuck email joe@joedrumgoole.com and I will try and help. 
