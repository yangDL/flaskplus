import sys
from flaskplus.flaskplus import *
from logic_tag import *

app = FlaskPlus(__name__)

@app.route('/tag_service/return_list', methods=['GET'])
def return_list():
    print(id(logging))
    print(id(app.logger))

    logging.info('I`m the main function');
    test()
    logging.info('app log')
    raise Exception('heh')
    
    return ['red', 'yellow', 'blue']


@app.route('/tag_service/return_map', methods=['GET'])
def return_map():
    return {'username': 'zhangnian', 'age': 18}


@app.route('/tag_service/return_logic_error', methods=['GET'])
def return_logic_error():
    # 注意，业务逻辑上的错误，code的值必须是正数！！！
    # 系统错误，code的值必须是负数，比如数据库查询失败，这种类型的错误框架已经处理了，所以一般不需要再APP代码中处理
    return make_error(101, '逻辑错误，比如找不到标签数据')


if __name__  == '__main__':
    app.run(host='0.0.0.0', port=89, debug=False)
