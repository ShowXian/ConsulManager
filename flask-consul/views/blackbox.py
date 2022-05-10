from flask import Blueprint
from flask_restful import reqparse, Resource, Api
from werkzeug.datastructures import  FileStorage
import sys

from units.input import with_open_file, read_execl

sys.path.append("..")
from units import token_auth,blackbox_manager

blueprint = Blueprint('blackbox',__name__)
api = Api(blueprint)

parser = reqparse.RequestParser()
parser.add_argument('module',type=str)
parser.add_argument('company',type=str)
parser.add_argument('project',type=str)
parser.add_argument('env',type=str)
parser.add_argument('name',type=str)
parser.add_argument('instance',type=str)
parser.add_argument('del_dict',type=dict)
parser.add_argument('up_dict',type=dict)
parser.add_argument('file',required=True, type=FileStorage, location="files", help="File is wrong.")


class GetAllList(Resource):
    @token_auth.auth.login_required
    def get(self):
        args = parser.parse_args()
        return blackbox_manager.get_all_list(args['module'],args['company'],args['project'],args['env'])

class GetConfig(Resource):
    @token_auth.auth.login_required
    def get(self, stype):
        if stype == 'rules':
            return blackbox_manager.get_rules()
        elif stype == 'bconfig':
            return blackbox_manager.get_bconfig()
        elif stype == 'pconfig':
            return blackbox_manager.get_pconfig()

class BlackboxApi(Resource):
    decorators = [token_auth.auth.login_required]
    def get(self):
        return blackbox_manager.get_service()
    def post(self):
        args = parser.parse_args()
        return blackbox_manager.add_service(args['module'],args['company'],args['project'],
                                            args['env'],args['name'],args['instance'])
    def put(self):
        args = parser.parse_args()
        del_dict = args['del_dict']
        up_dict = args['up_dict']
        resp_del = blackbox_manager.del_service(del_dict['module'],del_dict['company'],
                                                del_dict['project'],del_dict['env'],del_dict['name'])
        resp_add = blackbox_manager.add_service(up_dict['module'],up_dict['company'],up_dict['project'],
                                                up_dict['env'],up_dict['name'],up_dict['instance'])
        if resp_del["code"] == 20000 and resp_add["code"] == 20000:
            return {"code": 20000, "data": f"更新成功！"}
        else:
            return {"code": 50000, "data": f"更新失败！"}
    def delete(self):
        args = parser.parse_args()
        return blackbox_manager.del_service(args['module'],args['company'],args['project'],args['env'],args['name'])


"""
导入站点接口
"""
class Blackbox_Upload_Web(Resource):

    def post(self):
        file = parser.parse_args().get("file")
        try:
            file.save(file.filename)
            print(file.filename)
            read_execl(path=file.filename)
        except Exception as e:
            print("导入失败",e)
            return {"code": 40000, "data": f"导入失败！"}
        return {"code": 20000, "data": f"导入成功！"}



api.add_resource(GetAllList,'/api/blackbox/alllist')
api.add_resource(BlackboxApi, '/api/blackbox/service')
api.add_resource(GetConfig,'/api/blackboxcfg/<stype>')
api.add_resource(Blackbox_Upload_Web,'/api/blackboxcfg/upload_web')