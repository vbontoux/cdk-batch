# Welcome to your CDK Python project!

## CDK deploy order

```
$ cdk synth
```
````
cdk deploy SecretManagerStack --parameters gittoken=
```

```
cdk deploy EcrPipelineStack
```

```
cdk deploy BatchStack
```

```
cdk deploy EventStack
```
