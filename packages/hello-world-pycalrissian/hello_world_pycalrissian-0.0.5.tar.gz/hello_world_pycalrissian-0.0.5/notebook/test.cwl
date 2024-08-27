#!/usr/bin/env cwl-runner

$graph:
- class: Workflow
  label: A very simple Hello world app to submit a job using pycalrissian
  doc: A very simple Hello world app to submit a job using pycalrissian

  requirements:
  - class: ScatterFeatureRequirement
  - class: SubworkflowFeatureRequirement
  - class: MultipleInputFeatureRequirement

  inputs:
    input_name:
      doc: Name of a Person
      type: string

  outputs:
    log_message:
      type: Directory
      outputSource:
      - hello-workflow-step/log_message

  steps:
    hello-workflow-step:
      in:
        input_name: input_name
      run: '#hello-workflow-step'
      out:
      - log_message
  id: hello-world
- class: Workflow
  label: |-
    Create a simple python app to submit a job using `pycalrissian`. The app will only print a very basic hello world.
  doc: |-
    Create a simple python app to submit a job using `pycalrissian`. The app will only print a very basic hello world.

  requirements:
  - class: ScatterFeatureRequirement
  - class: SubworkflowFeatureRequirement

  inputs:
    input_name:
      doc: Name of a Person
      type: string

  outputs:
    log_message:
      type: Directory
      outputSource:
      - hello-main/log_message

  steps:
    hello-main:
      in:
        input_name: input_name
      run: '#hello'
      out:
      - log_message
  id: hello-workflow-step
- class: CommandLineTool

  requirements:
    DockerRequirement:
      dockerPull: hello:latest
    InlineJavascriptRequirement: {}
    ResourceRequirement:
      coresMax: 2
      ramMax: 2000
    ShellCommandRequirement: {}

  inputs:
    input_name:
      type: string

  outputs:
    log_message:
      type: Directory
      outputBinding:
        glob: .

  baseCommand:
  - hello-world-pycalrissian
  arguments: []
  id: hello
$namespaces:
  s: https://schema.org/
cwlVersion: v1.1
s:softwareVersion: 0.1.0
schemas:
- http://schema.org/version/9.0/schemaorg-current-http.rdf
