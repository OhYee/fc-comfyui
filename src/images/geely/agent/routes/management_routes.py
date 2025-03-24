from flask import Blueprint, Flask, request, jsonify

from services.management_service import ManagementService


class ManagementRoutes:

    def __init__(self):
        self.bp = Blueprint("management", __name__, url_prefix="/management")
        self.service = ManagementService()
        self.setup_routes()

    def register(self, app: Flask):
        app.register_blueprint(self.bp)

    # TODO: Runfunction -> /initialize & /management/* 配置http trigger匿名访问，防止拿到域名的人管控实例
    def setup_routes(self):

        @self.bp.post("/start")
        def start():
            # TODO: 异步
            snapshot = request.args.get('snapshot')
            self.service.start(snapshot)
            return jsonify({
                "status": "success",
                "message": "Successfully load snapshot and start backend process"
            }), 200

        @self.bp.post("/stop")
        def stop():
            self.service.stop()
            return jsonify({
                "status": "success",
                "message": "Successfully shutdown backend process"
            }), 200

        @self.bp.post("/save")
        def save():
            # TODO: 异步
            self.service.save()
            return jsonify({
                "status": "success",
                "message": "Successfully save snapshot"
            }), 200

        @self.bp.post("/saveAndStop")
        def save_and_stop():
            # TODO: 异步
            self.service.save_and_stop()
            return jsonify({
                "status": "success",
                "message": "Successfully save snapshot and stop backend process"
            }), 200

        # TODO 检查文件内容有更新的接口

        @self.bp.get("/status")
        def status():
            return jsonify({
                "data": self.service.status.value,
                "status": "success"
            }), 200

        @self.bp.get("/snapshots")
        def snapshots():
            return jsonify({
                "data": self.service.find_snapshots(),
                "status": "success"
            }), 200
