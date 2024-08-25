from os import path as os_path

from pydantic import BaseModel

PD_CONFIG_FILE = os_path.expanduser('~/.pdconfig.json')


class UserProfile(BaseModel):
    """Each user is uniquely identified by their username"""
    name: str | None = None  # User's name
    email: str | None = None  # User's email
    github: str | None = None  # GitHub username
    ssh_key: str | None = None  # SSH key path


class EnvVar(BaseModel):
    """Each environment variable is uniquely identified by its name"""
    key: str  # Environment variable name
    value: str  # Environment variable value


class Instance(BaseModel):
    """Each instance is uniquely identified by its ID"""
    id: str  # Instance ID
    ip: str  # Instance IP (e.g. Elastic IP)


class Project(BaseModel):
    """Each project is uniquely identified by its full path on disk"""
    type: str  # Type of project (e.g. react, fastapi)
    name: str  # Name of the project (e.g. project)
    path: str  # Full path on disk (e.g. /path/to/project)
    remote: str | None = None  # Remote path e.g. RE-LABS/ReX/rexhttp
    env: list[EnvVar] = []  # Environment variables
    pods: list[str] = 0  # Instances (e.g. EC2 instances)
    domain: str | None = None  # Domain name (e.g. example.com)


class Defaults(BaseModel):
    aws_launch_template: str  # Name of the default EC2 launch template
    aws_pem_key: str  # Path of the default EC2 PEM key
    aws_region: str  # Default EC2 region


class Pod(BaseModel):
    cluster_name: str | None
    instance_name: str
    instance_type: str
    key_name: str  # SSH key for the pod
    vpc_id: str
    subnet_id: str
    launch_template: str
    security_groups: dict[str, str]  # Name to Security Group
    private_dns: dict[str, str]  # Name to IP
    public_dns: dict[str, str] | None  # Name to IP


class AWS(BaseModel):
    access_key_id: str
    secret_access_key: str
    pods: dict[str, Pod]


class PDConfig(BaseModel):
    profile: UserProfile
    projects: list[Project]
    defaults: Defaults
    aws: AWS
