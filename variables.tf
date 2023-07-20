variable "region" {
  description = "The AWS region"
  
}

variable "start_resources_function" {
  description = "The name of the start resources function"
  default     = "liga_EC2"
}

variable "stop_resources_function" {
  description = "The name of the stop resources function"
  default     = "desliga_EC2"
}

