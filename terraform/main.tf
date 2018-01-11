provider "aws" {
  region = "eu-west-2"
}

data "template_file" "worker_bootstrap" {
  template = "${file("boot.sh.tlp")}"
  vars {
    is_worker = false
  }
}

data "template_file" "server_bootstrap" {
  template = "${file("boot.sh.tlp")}"
  vars {
    is_worker = true
  }
}


/* Server */
resource "aws_instance" "server" {
  ami                   = "ami-e7d6c983"
  instance_type         = "t2.small"	
  key_name              = "kubernetes.cluster.k8s.informaticslab.co.uk-be:87:08:3a:ea:a2:9e:7e:be:c1:97:2a:42:9b:8a:05"
  user_data             = "${data.template_file.server_bootstrap.rendered}"
  iam_instance_profile  = "seasia-bokeh-on-ec2"
  tags {
    Name = "se_asia_dis_vis_demo",
    EndOfLife = "2018-02-10",
    OfficeHours = false,
    Project = "SEAsia",
    ServiceCode = "ZZTLAB",
    ServiceOwner = "aws@informaticslab.co.uk",
    Owner = "theo.mccaie",
    Worker = false
  }
  security_groups        = ["default", "${aws_security_group.security_server.name}", "${aws_security_group.security_metoffice.name}", "${aws_security_group.security_gateway.name}", "${aws_security_group.notebook.name}", "${aws_security_group.dask_status.name}"]
}

resource "aws_security_group" "security_server" {
  name = "bokeh seasia security_server"
  description = "Allow web traffic to server"

  ingress {
      from_port = 80
      to_port = 8888
      protocol = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
      from_port = 0
      to_port = 0
      protocol = "-1"
      cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "notebook" {
  name = "bokeh_demo_notebook_seasia"
  description = "Allow port 8000"

  ingress {
      from_port = 8000
      to_port = 8000
      protocol = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "dask_status" {
  name = "bokeh_demo_dask_status_seasia"
  description = "Allow port 8787 for dask scheduler page"

  ingress {
      from_port = 8787
      to_port = 8787
      protocol = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
  }
}




resource "aws_security_group" "security_metoffice" {
  name = "seasia_bokeh_security_metoffice"
  description = "Allow ssh from Met Office IPs"

  ingress {
      from_port = 22
      to_port = 22
      protocol = "tcp"
      cidr_blocks = ["151.170.0.0/16"]
  }
}


resource "aws_security_group" "security_gateway" {
  name = "seasia_bokeh_security_gateway"
  description = "Allow ssh from gateway."

  ingress {
      from_port = 22
      to_port = 22
      protocol = "tcp"
      cidr_blocks = ["52.208.180.144/32"]
  }
}


resource "aws_security_group_rule" "worker_incoming" {
  type        = "ingress"
  from_port   = 0
  to_port     = 65535
  protocol    = "tcp"
  source_security_group_id = "${aws_security_group.worker.id}"
  security_group_id = "${aws_security_group.security_server.id}"
}



/* Worker */

resource "aws_launch_configuration" "workers" {
  # Amazon Linux ami
  image_id              = "ami-e7d6c983"
  instance_type         = "t2.small"  
  key_name              = "kubernetes.cluster.k8s.informaticslab.co.uk-be:87:08:3a:ea:a2:9e:7e:be:c1:97:2a:42:9b:8a:05"
  iam_instance_profile  = "seasia-bokeh-on-ec2"
  user_data             = "${data.template_file.worker_bootstrap.rendered}"
  security_groups        = ["default", "${aws_security_group.worker.name}", "${aws_security_group.security_metoffice.name}", "${aws_security_group.security_gateway.name}"]
  spot_price            = "0.015"
}


resource "aws_autoscaling_group" "worker" {
  name                  = "se_asia_dis_vis_demo_worker"
  availability_zones    = ["eu-west-2a", "eu-west-2b"]
  max_size              = 5
  min_size              = 1
  desired_capacity      = 3
  health_check_grace_period = 300
  health_check_type     = "EC2"
  force_delete          = true
  launch_configuration  = "${aws_launch_configuration.workers.name}"

  tag {
    key                 = "Name"
    value               =  "se_asia_dis_vis_demo_worker"
    propagate_at_launch = true
  }

  tag {
    key                 = "EndOfLife"
    value               = "2018-02-10"
    propagate_at_launch = true
  }

tag {
    key                 = "Owner"
    value               = "theo.mccaie"
    propagate_at_launch = true
  }

  tag {
    key                 = "Worker"
    value               = true
    propagate_at_launch = true
  }
}

resource "aws_security_group_rule" "server_incoming" {
  type        = "ingress"
  from_port   = 0
  to_port     = 65535
  protocol    = "tcp"
  source_security_group_id = "${aws_security_group.security_server.id}"
  security_group_id = "${aws_security_group.worker.id}"

}
resource "aws_security_group" "worker" {
  name = "sea_bokeh_worker"
}