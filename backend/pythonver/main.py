# -*- coding: utf-8 -*-
import os
import sys
from flask import Flask, request, jsonify
import logging

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)

# Configuration for both local and Cloud Run environments
class Config:
    def __init__(self):
        self.port = int(os.environ.get('PORT', 8080))
        self.host = '0.0.0.0'  # Required for Cloud Run
        self.debug = os.environ.get('FLASK_ENV') == 'development'
        self.service_name = os.environ.get('K_SERVICE', 'local-dev')
        self.revision = os.environ.get('K_REVISION', 'local-dev')
    
    def is_cloud_run(self):
        return 'K_SERVICE' in os.environ

config = Config()

# Main application route (converted from Cloud Function)
@app.route('/', methods=['GET', 'POST'])
def main_handler():
    """Main handler - converted from Cloud Function format"""
    try:
        if request.method == 'POST':
            request_json = request.get_json(silent=True)
            # Your original Cloud Function logic here
            
            # Fix the incomplete packages_html_list assignment
            packages_html_list = []  # Complete this assignment based on your needs
            
            return jsonify({
                'status': 'success',
                'data': packages_html_list,
                'service': config.service_name,
                'revision': config.revision
            })
        else:
            return jsonify({
                'message': 'Service is running',
                'environment': 'Cloud Run' if config.is_cloud_run() else 'Local Development',
                'service': config.service_name
            })
    except Exception as e:
        logging.error(f"Error in main handler: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Required health check endpoints for Cloud Run
@app.route('/health')
def health_check():
    """Liveness probe endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': int(os.time.time()),
        'service': config.service_name
    }), 200

@app.route('/ready') 
def readiness_check():
    """Startup probe endpoint"""
    # Add any initialization checks here
    return jsonify({
        'status': 'ready',
        'timestamp': int(os.time.time()),
        'service': config.service_name
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Cloud Run requires binding to 0.0.0.0 and using PORT env variable
    app.run(
        host=config.host,  # 0.0.0.0 required for Cloud Run
        port=config.port,  # PORT environment variable
        debug=config.debug
    )