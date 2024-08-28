r'''
# EC2/On-Premise Server Blue/Green Deployment Group construct

This construct creates a CodeDeploy Deployment Group for an EC2/On-Premises Deployment Group using the Blue/Green Deployment configuration.

**ATTENTION**: At the moment, this construct only supports the EC2 deployments with Auto Scaling Groups. The construct does not support neither the EC2 tag-based deployments nor the On-Premises tag-based deployments.

## Overview

Blue/Green deployments is popular deployment strategy that allows you to deploy your application to a new set of instances while keeping the old set of instances running. This allows you to switch traffic from the old set of instances to the new set of instances in a controlled manner.

This construct creates a CodeDeploy Deployment Group for an EC2 using the Blue/Green deployment configuration. The Deployment Group is associated with an Auto Scaling Group and a Load Balancer Target Group.

When a deployment is triggered, the Deployment Group will create a new Auto Scaling Group with the same configuration as the original Auto Scaling Group. The new Auto Scaling Group is called the Green Fleet. The Deployment Group will deploy the new revision of the application to the Green Fleet.
After the deployment is successful, the Deployment Group will switch the traffic from the original Auto Scaling Group (Blue Fleet) to the Green Fleet. The Deployment Group will then terminate the instances in the original Auto Scaling Group (if configured to do so).
The Deployment Group will wait for the original instances to be terminated before marking the deployment as successful.

You can configure the deployment to automatically rollback if the deployment fails, if the deployment is stopped, or if the deployment is in alarm.

## Installation

NPM package: https://www.npmjs.com/package/@otocolobus/aws-cdk-serverbluegreendeploymentgroup

```bash
npm install @otocolobus/aws-cdk-serverbluegreendeploymentgroup
```

PyPI package: https://pypi.org/project/aws-cdk-serverbluegreendeploymentgroup/

```bash
pip install aws-cdk-serverbluegreendeploymentgroup
```

## Usage

```python
import { ServerBlueGreenDeploymentGroup } from "@otocolobus/aws-cdk-serverbluegreendeploymentgroup";

class MyStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // ... other resources for LoadBalancer, AutoScalingGroup, etc.

    const application = new codedeploy.ServerApplication(this, "Application", {
      applicationName: "MyApplication",
    });

    // role required by CodeDeploy to do Blue/Green deployments with EC2 Auto Scaling Groups
    const role = new iam.Role(this, "Role", {
      assumedBy: new iam.ServicePrincipal("codedeploy.amazonaws.com"),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AWSCodeDeployRole"),
      ],
      inlinePolicies: {
        ASGWithLaunchTemplate: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              actions: [
                "ec2:CreateTags",
                "ec2:RunInstances",
                "iam:PassRole",
                "ssm:GetParameters",
              ],
              resources: ["*"],
            }),
          ],
        }),
      },
    });

    const deploymentGroup = new ServerBlueGreenDeploymentGroup(
      this,
      "DeploymentGroup",
      {
        application,
        deploymentGroupName: "DeploymentGroup",
        role,
        loadBalancers: [
          codedeploy.LoadBalancer.application(loadBalancerTargetGroup),
        ],
        autoScalingGroups,
        // ... other optional properties
      },
    );

    // ... other resources for CodeDeploy and CodePipeline
    // where buildOutput is the output of the CodeBuild action

    pipeline.addStage({
      stageName: "Deploy",
      actions: [
        new codepipeline_actions.CodeDeployServerDeployAction({
          actionName: "Deploy",
          input: buildOutput,
          deploymentGroup,
        });
      ],
    });
  }
}
```

## Limitations

Currently, it is not possible to update the Deployment Group name after the deployment group is created.
Currently, it is not possible to create a Deployment Group for an EC2 or On-Premises deployment with the tag-based configuration.

## Author

[Władysław Czyżewski](https://github.com/wladyslawczyzewski) (https://otocolobus.com)
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_autoscaling as _aws_cdk_aws_autoscaling_ceddda9d
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_codedeploy as _aws_cdk_aws_codedeploy_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d


@jsii.implements(_aws_cdk_aws_codedeploy_ceddda9d.IServerDeploymentGroup)
class ServerBlueGreenDeploymentGroup(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@otocolobus/aws-cdk-serverbluegreendeploymentgroup.ServerBlueGreenDeploymentGroup",
):
    def __init__(
        self,
        scope: _aws_cdk_ceddda9d.Stack,
        id: builtins.str,
        *,
        green_fleet_provision_option: typing.Optional[builtins.str] = None,
        manual_traffic_routing_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        original_instance_policy: typing.Optional[builtins.str] = None,
        terminate_original_instances_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        traffic_routing_config: typing.Optional[builtins.str] = None,
        alarms: typing.Optional[typing.Sequence[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]] = None,
        application: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IServerApplication] = None,
        auto_rollback: typing.Optional[typing.Union[_aws_cdk_aws_codedeploy_ceddda9d.AutoRollbackConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_scaling_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.IAutoScalingGroup]] = None,
        deployment_config: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IServerDeploymentConfig] = None,
        deployment_group_name: typing.Optional[builtins.str] = None,
        ec2_instance_tags: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.InstanceTagSet] = None,
        ignore_alarm_configuration: typing.Optional[builtins.bool] = None,
        ignore_poll_alarms_failure: typing.Optional[builtins.bool] = None,
        install_agent: typing.Optional[builtins.bool] = None,
        load_balancer: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.LoadBalancer] = None,
        load_balancers: typing.Optional[typing.Sequence[_aws_cdk_aws_codedeploy_ceddda9d.LoadBalancer]] = None,
        on_premise_instance_tags: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.InstanceTagSet] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        termination_hook: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param green_fleet_provision_option: How to provision the green fleet. Default: COPY_AUTO_SCALING_GROUP
        :param manual_traffic_routing_timeout: How long to wait for the manual traffic rerouting to complete. Default: - if ``trafficRoutingConfig`` is ``MANUALLY``, this is required - otherwise, this is ignored.
        :param original_instance_policy: The action to take on instances in the original environment after a successful blue/green deployment. Default: TERMINATE
        :param terminate_original_instances_timeout: How long to wait before terminating the original instances. Default: - if ``originalInstancePolicy`` is ``TERMINATE``, this is required - otherwise, this is ignored.
        :param traffic_routing_config: How to reroute traffic to the green fleet. Default: AUTOMATICALLY
        :param alarms: The CloudWatch alarms associated with this Deployment Group. CodeDeploy will stop (and optionally roll back) a deployment if during it any of the alarms trigger. Alarms can also be added after the Deployment Group is created using the ``#addAlarm`` method. Default: []
        :param application: The CodeDeploy EC2/on-premise Application this Deployment Group belongs to. Default: - A new Application will be created.
        :param auto_rollback: The auto-rollback configuration for this Deployment Group. Default: - default AutoRollbackConfig.
        :param auto_scaling_groups: The auto-scaling groups belonging to this Deployment Group. Auto-scaling groups can also be added after the Deployment Group is created using the ``#addAutoScalingGroup`` method. [disable-awslint:ref-via-interface] is needed because we update userdata for ASGs to install the codedeploy agent. Default: []
        :param deployment_config: The EC2/on-premise Deployment Configuration to use for this Deployment Group. Default: ServerDeploymentConfig#OneAtATime
        :param deployment_group_name: The physical, human-readable name of the CodeDeploy Deployment Group. Default: - An auto-generated name will be used.
        :param ec2_instance_tags: All EC2 instances matching the given set of tags when a deployment occurs will be added to this Deployment Group. Default: - No additional EC2 instances will be added to the Deployment Group.
        :param ignore_alarm_configuration: Whether to skip the step of checking CloudWatch alarms during the deployment process. Default: - false
        :param ignore_poll_alarms_failure: Whether to continue a deployment even if fetching the alarm status from CloudWatch failed. Default: false
        :param install_agent: If you've provided any auto-scaling groups with the ``#autoScalingGroups`` property, you can set this property to add User Data that installs the CodeDeploy agent on the instances. Default: true
        :param load_balancer: (deprecated) The load balancer to place in front of this Deployment Group. Can be created from either a classic Elastic Load Balancer, or an Application Load Balancer / Network Load Balancer Target Group. Default: - Deployment Group will not have a load balancer defined.
        :param load_balancers: CodeDeploy supports the deployment to multiple load balancers. Specify either multiple Classic Load Balancers, or Application Load Balancers / Network Load Balancers Target Groups. Default: - Deployment Group will not have load balancers defined.
        :param on_premise_instance_tags: All on-premise instances matching the given set of tags when a deployment occurs will be added to this Deployment Group. Default: - No additional on-premise instances will be added to the Deployment Group.
        :param role: The service Role of this Deployment Group. Default: - A new Role will be created.
        :param termination_hook: Indicates whether the deployment group was configured to have CodeDeploy install a termination hook into an Auto Scaling group. Default: - false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9e21d06c60add2ebacfef3f59c5d38d834640d2fc57a0b688b8d579ad7b6c8f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ServerBlueGreenDeploymentGroupProps(
            green_fleet_provision_option=green_fleet_provision_option,
            manual_traffic_routing_timeout=manual_traffic_routing_timeout,
            original_instance_policy=original_instance_policy,
            terminate_original_instances_timeout=terminate_original_instances_timeout,
            traffic_routing_config=traffic_routing_config,
            alarms=alarms,
            application=application,
            auto_rollback=auto_rollback,
            auto_scaling_groups=auto_scaling_groups,
            deployment_config=deployment_config,
            deployment_group_name=deployment_group_name,
            ec2_instance_tags=ec2_instance_tags,
            ignore_alarm_configuration=ignore_alarm_configuration,
            ignore_poll_alarms_failure=ignore_poll_alarms_failure,
            install_agent=install_agent,
            load_balancer=load_balancer,
            load_balancers=load_balancers,
            on_premise_instance_tags=on_premise_instance_tags,
            role=role,
            termination_hook=termination_hook,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="application")
    def application(self) -> _aws_cdk_aws_codedeploy_ceddda9d.IServerApplication:
        return typing.cast(_aws_cdk_aws_codedeploy_ceddda9d.IServerApplication, jsii.get(self, "application"))

    @builtins.property
    @jsii.member(jsii_name="deploymentConfig")
    def deployment_config(
        self,
    ) -> _aws_cdk_aws_codedeploy_ceddda9d.IServerDeploymentConfig:
        return typing.cast(_aws_cdk_aws_codedeploy_ceddda9d.IServerDeploymentConfig, jsii.get(self, "deploymentConfig"))

    @builtins.property
    @jsii.member(jsii_name="deploymentGroupArn")
    def deployment_group_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentGroupArn"))

    @builtins.property
    @jsii.member(jsii_name="deploymentGroupName")
    def deployment_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deploymentGroupName"))

    @builtins.property
    @jsii.member(jsii_name="autoScalingGroups")
    def auto_scaling_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_autoscaling_ceddda9d.IAutoScalingGroup]]:
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_autoscaling_ceddda9d.IAutoScalingGroup]], jsii.get(self, "autoScalingGroups"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "role"))


@jsii.data_type(
    jsii_type="@otocolobus/aws-cdk-serverbluegreendeploymentgroup.ServerBlueGreenDeploymentGroupProps",
    jsii_struct_bases=[_aws_cdk_aws_codedeploy_ceddda9d.ServerDeploymentGroupProps],
    name_mapping={
        "alarms": "alarms",
        "application": "application",
        "auto_rollback": "autoRollback",
        "auto_scaling_groups": "autoScalingGroups",
        "deployment_config": "deploymentConfig",
        "deployment_group_name": "deploymentGroupName",
        "ec2_instance_tags": "ec2InstanceTags",
        "ignore_alarm_configuration": "ignoreAlarmConfiguration",
        "ignore_poll_alarms_failure": "ignorePollAlarmsFailure",
        "install_agent": "installAgent",
        "load_balancer": "loadBalancer",
        "load_balancers": "loadBalancers",
        "on_premise_instance_tags": "onPremiseInstanceTags",
        "role": "role",
        "termination_hook": "terminationHook",
        "green_fleet_provision_option": "greenFleetProvisionOption",
        "manual_traffic_routing_timeout": "manualTrafficRoutingTimeout",
        "original_instance_policy": "originalInstancePolicy",
        "terminate_original_instances_timeout": "terminateOriginalInstancesTimeout",
        "traffic_routing_config": "trafficRoutingConfig",
    },
)
class ServerBlueGreenDeploymentGroupProps(
    _aws_cdk_aws_codedeploy_ceddda9d.ServerDeploymentGroupProps,
):
    def __init__(
        self,
        *,
        alarms: typing.Optional[typing.Sequence[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]] = None,
        application: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IServerApplication] = None,
        auto_rollback: typing.Optional[typing.Union[_aws_cdk_aws_codedeploy_ceddda9d.AutoRollbackConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_scaling_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.IAutoScalingGroup]] = None,
        deployment_config: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IServerDeploymentConfig] = None,
        deployment_group_name: typing.Optional[builtins.str] = None,
        ec2_instance_tags: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.InstanceTagSet] = None,
        ignore_alarm_configuration: typing.Optional[builtins.bool] = None,
        ignore_poll_alarms_failure: typing.Optional[builtins.bool] = None,
        install_agent: typing.Optional[builtins.bool] = None,
        load_balancer: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.LoadBalancer] = None,
        load_balancers: typing.Optional[typing.Sequence[_aws_cdk_aws_codedeploy_ceddda9d.LoadBalancer]] = None,
        on_premise_instance_tags: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.InstanceTagSet] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        termination_hook: typing.Optional[builtins.bool] = None,
        green_fleet_provision_option: typing.Optional[builtins.str] = None,
        manual_traffic_routing_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        original_instance_policy: typing.Optional[builtins.str] = None,
        terminate_original_instances_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        traffic_routing_config: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alarms: The CloudWatch alarms associated with this Deployment Group. CodeDeploy will stop (and optionally roll back) a deployment if during it any of the alarms trigger. Alarms can also be added after the Deployment Group is created using the ``#addAlarm`` method. Default: []
        :param application: The CodeDeploy EC2/on-premise Application this Deployment Group belongs to. Default: - A new Application will be created.
        :param auto_rollback: The auto-rollback configuration for this Deployment Group. Default: - default AutoRollbackConfig.
        :param auto_scaling_groups: The auto-scaling groups belonging to this Deployment Group. Auto-scaling groups can also be added after the Deployment Group is created using the ``#addAutoScalingGroup`` method. [disable-awslint:ref-via-interface] is needed because we update userdata for ASGs to install the codedeploy agent. Default: []
        :param deployment_config: The EC2/on-premise Deployment Configuration to use for this Deployment Group. Default: ServerDeploymentConfig#OneAtATime
        :param deployment_group_name: The physical, human-readable name of the CodeDeploy Deployment Group. Default: - An auto-generated name will be used.
        :param ec2_instance_tags: All EC2 instances matching the given set of tags when a deployment occurs will be added to this Deployment Group. Default: - No additional EC2 instances will be added to the Deployment Group.
        :param ignore_alarm_configuration: Whether to skip the step of checking CloudWatch alarms during the deployment process. Default: - false
        :param ignore_poll_alarms_failure: Whether to continue a deployment even if fetching the alarm status from CloudWatch failed. Default: false
        :param install_agent: If you've provided any auto-scaling groups with the ``#autoScalingGroups`` property, you can set this property to add User Data that installs the CodeDeploy agent on the instances. Default: true
        :param load_balancer: (deprecated) The load balancer to place in front of this Deployment Group. Can be created from either a classic Elastic Load Balancer, or an Application Load Balancer / Network Load Balancer Target Group. Default: - Deployment Group will not have a load balancer defined.
        :param load_balancers: CodeDeploy supports the deployment to multiple load balancers. Specify either multiple Classic Load Balancers, or Application Load Balancers / Network Load Balancers Target Groups. Default: - Deployment Group will not have load balancers defined.
        :param on_premise_instance_tags: All on-premise instances matching the given set of tags when a deployment occurs will be added to this Deployment Group. Default: - No additional on-premise instances will be added to the Deployment Group.
        :param role: The service Role of this Deployment Group. Default: - A new Role will be created.
        :param termination_hook: Indicates whether the deployment group was configured to have CodeDeploy install a termination hook into an Auto Scaling group. Default: - false
        :param green_fleet_provision_option: How to provision the green fleet. Default: COPY_AUTO_SCALING_GROUP
        :param manual_traffic_routing_timeout: How long to wait for the manual traffic rerouting to complete. Default: - if ``trafficRoutingConfig`` is ``MANUALLY``, this is required - otherwise, this is ignored.
        :param original_instance_policy: The action to take on instances in the original environment after a successful blue/green deployment. Default: TERMINATE
        :param terminate_original_instances_timeout: How long to wait before terminating the original instances. Default: - if ``originalInstancePolicy`` is ``TERMINATE``, this is required - otherwise, this is ignored.
        :param traffic_routing_config: How to reroute traffic to the green fleet. Default: AUTOMATICALLY
        '''
        if isinstance(auto_rollback, dict):
            auto_rollback = _aws_cdk_aws_codedeploy_ceddda9d.AutoRollbackConfig(**auto_rollback)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22036542f2776c075076c91c0f396d3cddee1da9525773bec09a4157ec8e91eb)
            check_type(argname="argument alarms", value=alarms, expected_type=type_hints["alarms"])
            check_type(argname="argument application", value=application, expected_type=type_hints["application"])
            check_type(argname="argument auto_rollback", value=auto_rollback, expected_type=type_hints["auto_rollback"])
            check_type(argname="argument auto_scaling_groups", value=auto_scaling_groups, expected_type=type_hints["auto_scaling_groups"])
            check_type(argname="argument deployment_config", value=deployment_config, expected_type=type_hints["deployment_config"])
            check_type(argname="argument deployment_group_name", value=deployment_group_name, expected_type=type_hints["deployment_group_name"])
            check_type(argname="argument ec2_instance_tags", value=ec2_instance_tags, expected_type=type_hints["ec2_instance_tags"])
            check_type(argname="argument ignore_alarm_configuration", value=ignore_alarm_configuration, expected_type=type_hints["ignore_alarm_configuration"])
            check_type(argname="argument ignore_poll_alarms_failure", value=ignore_poll_alarms_failure, expected_type=type_hints["ignore_poll_alarms_failure"])
            check_type(argname="argument install_agent", value=install_agent, expected_type=type_hints["install_agent"])
            check_type(argname="argument load_balancer", value=load_balancer, expected_type=type_hints["load_balancer"])
            check_type(argname="argument load_balancers", value=load_balancers, expected_type=type_hints["load_balancers"])
            check_type(argname="argument on_premise_instance_tags", value=on_premise_instance_tags, expected_type=type_hints["on_premise_instance_tags"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument termination_hook", value=termination_hook, expected_type=type_hints["termination_hook"])
            check_type(argname="argument green_fleet_provision_option", value=green_fleet_provision_option, expected_type=type_hints["green_fleet_provision_option"])
            check_type(argname="argument manual_traffic_routing_timeout", value=manual_traffic_routing_timeout, expected_type=type_hints["manual_traffic_routing_timeout"])
            check_type(argname="argument original_instance_policy", value=original_instance_policy, expected_type=type_hints["original_instance_policy"])
            check_type(argname="argument terminate_original_instances_timeout", value=terminate_original_instances_timeout, expected_type=type_hints["terminate_original_instances_timeout"])
            check_type(argname="argument traffic_routing_config", value=traffic_routing_config, expected_type=type_hints["traffic_routing_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alarms is not None:
            self._values["alarms"] = alarms
        if application is not None:
            self._values["application"] = application
        if auto_rollback is not None:
            self._values["auto_rollback"] = auto_rollback
        if auto_scaling_groups is not None:
            self._values["auto_scaling_groups"] = auto_scaling_groups
        if deployment_config is not None:
            self._values["deployment_config"] = deployment_config
        if deployment_group_name is not None:
            self._values["deployment_group_name"] = deployment_group_name
        if ec2_instance_tags is not None:
            self._values["ec2_instance_tags"] = ec2_instance_tags
        if ignore_alarm_configuration is not None:
            self._values["ignore_alarm_configuration"] = ignore_alarm_configuration
        if ignore_poll_alarms_failure is not None:
            self._values["ignore_poll_alarms_failure"] = ignore_poll_alarms_failure
        if install_agent is not None:
            self._values["install_agent"] = install_agent
        if load_balancer is not None:
            self._values["load_balancer"] = load_balancer
        if load_balancers is not None:
            self._values["load_balancers"] = load_balancers
        if on_premise_instance_tags is not None:
            self._values["on_premise_instance_tags"] = on_premise_instance_tags
        if role is not None:
            self._values["role"] = role
        if termination_hook is not None:
            self._values["termination_hook"] = termination_hook
        if green_fleet_provision_option is not None:
            self._values["green_fleet_provision_option"] = green_fleet_provision_option
        if manual_traffic_routing_timeout is not None:
            self._values["manual_traffic_routing_timeout"] = manual_traffic_routing_timeout
        if original_instance_policy is not None:
            self._values["original_instance_policy"] = original_instance_policy
        if terminate_original_instances_timeout is not None:
            self._values["terminate_original_instances_timeout"] = terminate_original_instances_timeout
        if traffic_routing_config is not None:
            self._values["traffic_routing_config"] = traffic_routing_config

    @builtins.property
    def alarms(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]]:
        '''The CloudWatch alarms associated with this Deployment Group.

        CodeDeploy will stop (and optionally roll back)
        a deployment if during it any of the alarms trigger.

        Alarms can also be added after the Deployment Group is created using the ``#addAlarm`` method.

        :default: []

        :see: https://docs.aws.amazon.com/codedeploy/latest/userguide/monitoring-create-alarms.html
        '''
        result = self._values.get("alarms")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]], result)

    @builtins.property
    def application(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IServerApplication]:
        '''The CodeDeploy EC2/on-premise Application this Deployment Group belongs to.

        :default: - A new Application will be created.
        '''
        result = self._values.get("application")
        return typing.cast(typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IServerApplication], result)

    @builtins.property
    def auto_rollback(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.AutoRollbackConfig]:
        '''The auto-rollback configuration for this Deployment Group.

        :default: - default AutoRollbackConfig.
        '''
        result = self._values.get("auto_rollback")
        return typing.cast(typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.AutoRollbackConfig], result)

    @builtins.property
    def auto_scaling_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_autoscaling_ceddda9d.IAutoScalingGroup]]:
        '''The auto-scaling groups belonging to this Deployment Group.

        Auto-scaling groups can also be added after the Deployment Group is created
        using the ``#addAutoScalingGroup`` method.

        [disable-awslint:ref-via-interface] is needed because we update userdata
        for ASGs to install the codedeploy agent.

        :default: []
        '''
        result = self._values.get("auto_scaling_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_autoscaling_ceddda9d.IAutoScalingGroup]], result)

    @builtins.property
    def deployment_config(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IServerDeploymentConfig]:
        '''The EC2/on-premise Deployment Configuration to use for this Deployment Group.

        :default: ServerDeploymentConfig#OneAtATime
        '''
        result = self._values.get("deployment_config")
        return typing.cast(typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IServerDeploymentConfig], result)

    @builtins.property
    def deployment_group_name(self) -> typing.Optional[builtins.str]:
        '''The physical, human-readable name of the CodeDeploy Deployment Group.

        :default: - An auto-generated name will be used.
        '''
        result = self._values.get("deployment_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ec2_instance_tags(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.InstanceTagSet]:
        '''All EC2 instances matching the given set of tags when a deployment occurs will be added to this Deployment Group.

        :default: - No additional EC2 instances will be added to the Deployment Group.
        '''
        result = self._values.get("ec2_instance_tags")
        return typing.cast(typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.InstanceTagSet], result)

    @builtins.property
    def ignore_alarm_configuration(self) -> typing.Optional[builtins.bool]:
        '''Whether to skip the step of checking CloudWatch alarms during the deployment process.

        :default: - false
        '''
        result = self._values.get("ignore_alarm_configuration")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ignore_poll_alarms_failure(self) -> typing.Optional[builtins.bool]:
        '''Whether to continue a deployment even if fetching the alarm status from CloudWatch failed.

        :default: false
        '''
        result = self._values.get("ignore_poll_alarms_failure")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def install_agent(self) -> typing.Optional[builtins.bool]:
        '''If you've provided any auto-scaling groups with the ``#autoScalingGroups`` property, you can set this property to add User Data that installs the CodeDeploy agent on the instances.

        :default: true

        :see: https://docs.aws.amazon.com/codedeploy/latest/userguide/codedeploy-agent-operations-install.html
        '''
        result = self._values.get("install_agent")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def load_balancer(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.LoadBalancer]:
        '''(deprecated) The load balancer to place in front of this Deployment Group.

        Can be created from either a classic Elastic Load Balancer,
        or an Application Load Balancer / Network Load Balancer Target Group.

        :default: - Deployment Group will not have a load balancer defined.

        :deprecated: - Use ``loadBalancers`` instead.

        :stability: deprecated
        '''
        result = self._values.get("load_balancer")
        return typing.cast(typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.LoadBalancer], result)

    @builtins.property
    def load_balancers(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_codedeploy_ceddda9d.LoadBalancer]]:
        '''CodeDeploy supports the deployment to multiple load balancers.

        Specify either multiple Classic Load Balancers, or
        Application Load Balancers / Network Load Balancers Target Groups.

        :default: - Deployment Group will not have load balancers defined.
        '''
        result = self._values.get("load_balancers")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_codedeploy_ceddda9d.LoadBalancer]], result)

    @builtins.property
    def on_premise_instance_tags(
        self,
    ) -> typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.InstanceTagSet]:
        '''All on-premise instances matching the given set of tags when a deployment occurs will be added to this Deployment Group.

        :default: - No additional on-premise instances will be added to the Deployment Group.
        '''
        result = self._values.get("on_premise_instance_tags")
        return typing.cast(typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.InstanceTagSet], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''The service Role of this Deployment Group.

        :default: - A new Role will be created.
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def termination_hook(self) -> typing.Optional[builtins.bool]:
        '''Indicates whether the deployment group was configured to have CodeDeploy install a termination hook into an Auto Scaling group.

        :default: - false

        :see: https://docs.aws.amazon.com/codedeploy/latest/userguide/integrations-aws-auto-scaling.html#integrations-aws-auto-scaling-behaviors
        '''
        result = self._values.get("termination_hook")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def green_fleet_provision_option(self) -> typing.Optional[builtins.str]:
        '''How to provision the green fleet.

        :default: COPY_AUTO_SCALING_GROUP
        '''
        result = self._values.get("green_fleet_provision_option")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def manual_traffic_routing_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''How long to wait for the manual traffic rerouting to complete.

        :default:

        - if ``trafficRoutingConfig`` is ``MANUALLY``, this is required
        - otherwise, this is ignored.
        '''
        result = self._values.get("manual_traffic_routing_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def original_instance_policy(self) -> typing.Optional[builtins.str]:
        '''The action to take on instances in the original environment after a successful blue/green deployment.

        :default: TERMINATE
        '''
        result = self._values.get("original_instance_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def terminate_original_instances_timeout(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''How long to wait before terminating the original instances.

        :default:

        - if ``originalInstancePolicy`` is ``TERMINATE``, this is required
        - otherwise, this is ignored.
        '''
        result = self._values.get("terminate_original_instances_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def traffic_routing_config(self) -> typing.Optional[builtins.str]:
        '''How to reroute traffic to the green fleet.

        :default: AUTOMATICALLY
        '''
        result = self._values.get("traffic_routing_config")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServerBlueGreenDeploymentGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ServerBlueGreenDeploymentGroup",
    "ServerBlueGreenDeploymentGroupProps",
]

publication.publish()

def _typecheckingstub__b9e21d06c60add2ebacfef3f59c5d38d834640d2fc57a0b688b8d579ad7b6c8f(
    scope: _aws_cdk_ceddda9d.Stack,
    id: builtins.str,
    *,
    green_fleet_provision_option: typing.Optional[builtins.str] = None,
    manual_traffic_routing_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    original_instance_policy: typing.Optional[builtins.str] = None,
    terminate_original_instances_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    traffic_routing_config: typing.Optional[builtins.str] = None,
    alarms: typing.Optional[typing.Sequence[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]] = None,
    application: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IServerApplication] = None,
    auto_rollback: typing.Optional[typing.Union[_aws_cdk_aws_codedeploy_ceddda9d.AutoRollbackConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    auto_scaling_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.IAutoScalingGroup]] = None,
    deployment_config: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IServerDeploymentConfig] = None,
    deployment_group_name: typing.Optional[builtins.str] = None,
    ec2_instance_tags: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.InstanceTagSet] = None,
    ignore_alarm_configuration: typing.Optional[builtins.bool] = None,
    ignore_poll_alarms_failure: typing.Optional[builtins.bool] = None,
    install_agent: typing.Optional[builtins.bool] = None,
    load_balancer: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.LoadBalancer] = None,
    load_balancers: typing.Optional[typing.Sequence[_aws_cdk_aws_codedeploy_ceddda9d.LoadBalancer]] = None,
    on_premise_instance_tags: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.InstanceTagSet] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    termination_hook: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22036542f2776c075076c91c0f396d3cddee1da9525773bec09a4157ec8e91eb(
    *,
    alarms: typing.Optional[typing.Sequence[_aws_cdk_aws_cloudwatch_ceddda9d.IAlarm]] = None,
    application: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IServerApplication] = None,
    auto_rollback: typing.Optional[typing.Union[_aws_cdk_aws_codedeploy_ceddda9d.AutoRollbackConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    auto_scaling_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_autoscaling_ceddda9d.IAutoScalingGroup]] = None,
    deployment_config: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.IServerDeploymentConfig] = None,
    deployment_group_name: typing.Optional[builtins.str] = None,
    ec2_instance_tags: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.InstanceTagSet] = None,
    ignore_alarm_configuration: typing.Optional[builtins.bool] = None,
    ignore_poll_alarms_failure: typing.Optional[builtins.bool] = None,
    install_agent: typing.Optional[builtins.bool] = None,
    load_balancer: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.LoadBalancer] = None,
    load_balancers: typing.Optional[typing.Sequence[_aws_cdk_aws_codedeploy_ceddda9d.LoadBalancer]] = None,
    on_premise_instance_tags: typing.Optional[_aws_cdk_aws_codedeploy_ceddda9d.InstanceTagSet] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    termination_hook: typing.Optional[builtins.bool] = None,
    green_fleet_provision_option: typing.Optional[builtins.str] = None,
    manual_traffic_routing_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    original_instance_policy: typing.Optional[builtins.str] = None,
    terminate_original_instances_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    traffic_routing_config: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
