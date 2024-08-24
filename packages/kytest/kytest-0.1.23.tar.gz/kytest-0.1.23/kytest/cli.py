import click
from . import __version__
from .scaffold import create_scaffold
from .case_generator import generate


@click.group()
@click.version_option(version=__version__, help="Show version.")
# 老是变，等最后定下来再搞，目前也没啥用
def main():
    pass


@main.command()
@click.option('-p', '--platform', help="Specify the platform.")
def create(platform):
    """
    创建新项目
    @param platform: 平台，如api、android、ios、web
    @return:
    """
    create_scaffold(platform)


@main.command()
@click.option('-h', '--host', help="Specify the host.")
@click.option('-p', '--project', help='Specify the project.')
@click.option('-c', '--controller', default=None, help="Specify the controller.")
def generate(host, project, controller):
    """
    在当前目录生成用例，有相同的则进行覆盖
    @param host: tms服务的域名
    @param project: tms导入的接口项目
    @param controller：指定生成哪个controller，不指定就生成所有的controller，有空格需要用引号包括
    @return:
    """
    generate(host, project, controller)
