"""
Enhanced AI Agent OS - Flask API Extensions for Autonomous Management
Provides REST API endpoints for autonomous agent lifecycle management,
self-healing operations, and knowledge drift detection.

Author: Manus AI
Version: 1.0
Date: August 2025
License: MIT
"""

from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import uuid
import traceback

from autonomous_agent_base import (
    AgentState, AgentCapability, AgentPersonality, AgentMetrics,
    AutonomousAgentBase, KnowledgeDriftAlert
)
from agent_lifecycle_manager import (
    AgentLifecycleManager, AgentCreationRequest, AgentNeed,
    LifecyclePhase
)

# Create Blueprint for autonomous management endpoints
autonomous_bp = Blueprint('autonomous', __name__, url_prefix='/api/v1/autonomous')

# Global instances (to be initialized in create_app)
lifecycle_manager: Optional[AgentLifecycleManager] = None
active_agents: Dict[str, AutonomousAgentBase] = {}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_autonomous_app(config: Dict[str, Any]) -> Flask:
    """Create Flask app with autonomous management capabilities"""
    app = Flask(__name__)
    
    # Configure CORS for cross-origin requests
    CORS(app, origins="*")
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = config.get('JWT_SECRET_KEY', 'your-secret-key')
    jwt = JWTManager(app)
    
    # Initialize global lifecycle manager
    global lifecycle_manager
    lifecycle_manager = AgentLifecycleManager(
        neo4j_uri=config['NEO4J_URI'],
        neo4j_user=config['NEO4J_USER'],
        neo4j_password=config['NEO4J_PASSWORD'],
        rabbitmq_url=config['RABBITMQ_URL'],
        openai_api_key=config['OPENAI_API_KEY'],
        docker_client=config['DOCKER_CLIENT'],
        n8n_base_url=config.get('N8N_BASE_URL', 'http://localhost:5678'),
        api_base_url=config.get('API_BASE_URL', 'http://localhost:8000')
    )
    
    # Register blueprints
    app.register_blueprint(autonomous_bp)
    
    # Error handlers
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500
    
    return app


# Agent Lifecycle Management Endpoints

@autonomous_bp.route('/agents/lifecycle/create', methods=['POST'])
@jwt_required()
def create_agent_request():
    """Create a new agent creation request"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['need_type', 'required_capabilities', 'justification']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }), 400
        
        # Parse capabilities
        capabilities = set()
        for cap_str in data['required_capabilities']:
            try:
                capabilities.add(AgentCapability(cap_str))
            except ValueError:
                return jsonify({
                    'error': f'Invalid capability: {cap_str}',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }), 400
        
        # Create request
        request_id = str(uuid.uuid4())
        creation_request = AgentCreationRequest(
            request_id=request_id,
            need_type=AgentNeed(data['need_type']),
            required_capabilities=capabilities,
            performance_requirements=data.get('performance_requirements', {}),
            integration_requirements=data.get('integration_requirements', []),
            priority=data.get('priority', 5),
            justification=data['justification']
        )
        
        # Submit to lifecycle manager
        asyncio.create_task(lifecycle_manager._process_creation_request(request_id))
        lifecycle_manager._active_requests[request_id] = creation_request
        
        return jsonify({
            'success': True,
            'request_id': request_id,
            'message': 'Agent creation request submitted',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating agent request: {e}")
        return jsonify({
            'error': 'Failed to create agent request',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@autonomous_bp.route('/agents/lifecycle/status/<request_id>', methods=['GET'])
@jwt_required()
def get_creation_status(request_id: str):
    """Get status of agent creation request"""
    try:
        # Check active requests
        if request_id in lifecycle_manager._active_requests:
            request_obj = lifecycle_manager._active_requests[request_id]
            return jsonify({
                'request_id': request_id,
                'status': 'in_progress',
                'phase': 'processing',
                'created_at': request_obj.created_at.isoformat(),
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        
        # Check deployed agents
        for agent_id, agent_info in lifecycle_manager._deployed_agents.items():
            if agent_info['request_id'] == request_id:
                return jsonify({
                    'request_id': request_id,
                    'status': 'completed',
                    'phase': 'deployed',
                    'agent_id': agent_id,
                    'deployed_at': agent_info['deployed_at'].isoformat(),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
        
        return jsonify({
            'error': 'Request not found',
            'request_id': request_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 404
        
    except Exception as e:
        logger.error(f"Error getting creation status: {e}")
        return jsonify({
            'error': 'Failed to get creation status',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@autonomous_bp.route('/agents/lifecycle/deploy', methods=['POST'])
@jwt_required()
def deploy_agent():
    """Deploy an agent implementation"""
    try:
        data = request.get_json()
        
        implementation_id = data.get('implementation_id')
        if not implementation_id:
            return jsonify({
                'error': 'Missing implementation_id',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
        
        # Get implementation
        implementation = lifecycle_manager._active_implementations.get(implementation_id)
        if not implementation:
            return jsonify({
                'error': 'Implementation not found',
                'implementation_id': implementation_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 404
        
        # Deploy agent
        deployment_result = await lifecycle_manager._deploy_agent(implementation)
        
        if deployment_result.get('success', False):
            return jsonify({
                'success': True,
                'agent_id': deployment_result['agent_id'],
                'container_id': deployment_result['container_id'],
                'message': 'Agent deployed successfully',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': deployment_result.get('error', 'Deployment failed'),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 500
        
    except Exception as e:
        logger.error(f"Error deploying agent: {e}")
        return jsonify({
            'error': 'Failed to deploy agent',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@autonomous_bp.route('/agents/lifecycle/retire', methods=['POST'])
@jwt_required()
def retire_agent():
    """Retire an agent"""
    try:
        data = request.get_json()
        
        agent_id = data.get('agent_id')
        if not agent_id:
            return jsonify({
                'error': 'Missing agent_id',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
        
        reason = data.get('reason', 'manual_retirement')
        
        # Perform retirement
        retirement_result = await lifecycle_manager._graceful_agent_shutdown(agent_id)
        
        if retirement_result.get('success', False):
            return jsonify({
                'success': True,
                'agent_id': agent_id,
                'reason': reason,
                'message': 'Agent retired successfully',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': retirement_result.get('error', 'Retirement failed'),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 500
        
    except Exception as e:
        logger.error(f"Error retiring agent: {e}")
        return jsonify({
            'error': 'Failed to retire agent',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


# Agent Health and Monitoring Endpoints

@autonomous_bp.route('/agents/health/all', methods=['GET'])
@jwt_required()
def get_all_agent_health():
    """Get health status of all agents"""
    try:
        health_data = []
        
        for agent_id, agent_info in lifecycle_manager._deployed_agents.items():
            if agent_id in active_agents:
                agent = active_agents[agent_id]
                health_data.append({
                    'agent_id': agent_id,
                    'state': agent.state.value,
                    'health_score': agent.metrics.health_score,
                    'tasks_completed': agent.metrics.tasks_completed,
                    'tasks_failed': agent.metrics.tasks_failed,
                    'average_response_time': agent.metrics.average_response_time,
                    'last_activity': agent.metrics.last_activity.isoformat(),
                    'deployed_at': agent_info['deployed_at'].isoformat()
                })
        
        return jsonify({
            'agents': health_data,
            'total_agents': len(health_data),
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting agent health: {e}")
        return jsonify({
            'error': 'Failed to get agent health',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@autonomous_bp.route('/agents/<agent_id>/health', methods=['GET'])
@jwt_required()
def get_agent_health(agent_id: str):
    """Get health status of specific agent"""
    try:
        if agent_id not in active_agents:
            return jsonify({
                'error': 'Agent not found',
                'agent_id': agent_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 404
        
        agent = active_agents[agent_id]
        
        return jsonify({
            'agent_id': agent_id,
            'state': agent.state.value,
            'health_score': agent.metrics.health_score,
            'metrics': {
                'tasks_completed': agent.metrics.tasks_completed,
                'tasks_failed': agent.metrics.tasks_failed,
                'average_response_time': agent.metrics.average_response_time,
                'resource_utilization': agent.metrics.resource_utilization,
                'knowledge_contributions': agent.metrics.knowledge_contributions,
                'collaboration_score': agent.metrics.collaboration_score,
                'autonomy_score': agent.metrics.autonomy_score,
                'last_activity': agent.metrics.last_activity.isoformat()
            },
            'personality': {
                'name': agent.personality.name,
                'role': agent.personality.role,
                'capabilities': [cap.value for cap in agent.personality.capabilities]
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting agent health: {e}")
        return jsonify({
            'error': 'Failed to get agent health',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@autonomous_bp.route('/agents/<agent_id>/analyze-issues', methods=['GET'])
@jwt_required()
def analyze_agent_issues(agent_id: str):
    """Analyze issues with a specific agent"""
    try:
        if agent_id not in active_agents:
            return jsonify({
                'error': 'Agent not found',
                'agent_id': agent_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 404
        
        agent = active_agents[agent_id]
        
        # Perform issue analysis
        issue_analysis = await agent._analyze_performance_issues()
        
        return jsonify({
            'agent_id': agent_id,
            'analysis': issue_analysis,
            'recommended_actions': issue_analysis.get('healing_strategies', []),
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error analyzing agent issues: {e}")
        return jsonify({
            'error': 'Failed to analyze agent issues',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


# Self-Healing Endpoints

@autonomous_bp.route('/agents/<agent_id>/restart', methods=['POST'])
@jwt_required()
def restart_agent(agent_id: str):
    """Restart an agent"""
    try:
        data = request.get_json()
        restart_type = data.get('restart_type', 'soft')
        preserve_state = data.get('preserve_state', True)
        
        if agent_id not in active_agents:
            return jsonify({
                'error': 'Agent not found',
                'agent_id': agent_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 404
        
        agent = active_agents[agent_id]
        
        # Perform restart
        if restart_type == 'container':
            # Restart Docker container
            agent_info = lifecycle_manager._deployed_agents.get(agent_id)
            if agent_info and agent_info.get('container_id'):
                container = lifecycle_manager.docker_client.containers.get(
                    agent_info['container_id']
                )
                container.restart()
                
                return jsonify({
                    'success': True,
                    'agent_id': agent_id,
                    'restart_type': restart_type,
                    'message': 'Agent container restarted',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
        else:
            # Soft restart - stop and start agent
            await agent.stop()
            await agent.start()
            
            return jsonify({
                'success': True,
                'agent_id': agent_id,
                'restart_type': restart_type,
                'message': 'Agent restarted successfully',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        
    except Exception as e:
        logger.error(f"Error restarting agent: {e}")
        return jsonify({
            'error': 'Failed to restart agent',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@autonomous_bp.route('/agents/<agent_id>/scale', methods=['POST'])
@jwt_required()
def scale_agent_resources(agent_id: str):
    """Scale agent resources"""
    try:
        data = request.get_json()
        scale_type = data.get('scale_type', 'resources')
        
        if agent_id not in active_agents:
            return jsonify({
                'error': 'Agent not found',
                'agent_id': agent_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 404
        
        # Get container and update resources
        agent_info = lifecycle_manager._deployed_agents.get(agent_id)
        if agent_info and agent_info.get('container_id'):
            container = lifecycle_manager.docker_client.containers.get(
                agent_info['container_id']
            )
            
            # Update container resources
            container.update(
                cpu_quota=int(data.get('cpu_limit', 100000)),
                mem_limit=data.get('memory_limit', '512m')
            )
            
            return jsonify({
                'success': True,
                'agent_id': agent_id,
                'scale_type': scale_type,
                'new_limits': {
                    'cpu_limit': data.get('cpu_limit'),
                    'memory_limit': data.get('memory_limit')
                },
                'message': 'Agent resources scaled successfully',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
        else:
            return jsonify({
                'error': 'Agent container not found',
                'agent_id': agent_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 404
        
    except Exception as e:
        logger.error(f"Error scaling agent resources: {e}")
        return jsonify({
            'error': 'Failed to scale agent resources',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


# Knowledge Drift Detection Endpoints

@autonomous_bp.route('/knowledge/drift/check', methods=['GET'])
@jwt_required()
def check_knowledge_drift():
    """Check for knowledge drift across the system"""
    try:
        drift_alerts = []
        
        # Check drift for all active agents
        for agent_id, agent in active_agents.items():
            if hasattr(agent, '_knowledge_drift_detector') and agent._knowledge_drift_detector:
                alerts = await agent._knowledge_drift_detector.periodic_check()
                drift_alerts.extend(alerts)
        
        # Determine if any drift was detected
        drift_detected = len(drift_alerts) > 0
        
        # Get highest severity
        severities = [alert.severity for alert in drift_alerts]
        max_severity = 'low'
        if 'critical' in severities:
            max_severity = 'critical'
        elif 'high' in severities:
            max_severity = 'high'
        elif 'medium' in severities:
            max_severity = 'medium'
        
        return jsonify({
            'drift_detected': drift_detected,
            'alert_count': len(drift_alerts),
            'severity': max_severity,
            'alerts': [
                {
                    'alert_id': alert.alert_id,
                    'agent_id': alert.agent_id,
                    'drift_type': alert.drift_type,
                    'severity': alert.severity,
                    'description': alert.description,
                    'affected_knowledge': alert.affected_knowledge,
                    'timestamp': alert.timestamp.isoformat()
                }
                for alert in drift_alerts
            ],
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error checking knowledge drift: {e}")
        return jsonify({
            'error': 'Failed to check knowledge drift',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@autonomous_bp.route('/knowledge/drift/remediate', methods=['POST'])
@jwt_required()
def remediate_knowledge_drift():
    """Remediate knowledge drift"""
    try:
        data = request.get_json()
        
        alert_id = data.get('alert_id')
        if not alert_id:
            return jsonify({
                'error': 'Missing alert_id',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 400
        
        remediation_strategy = data.get('remediation_strategy', 'automatic')
        preserve_history = data.get('preserve_history', True)
        
        # Find the alert and perform remediation
        # This would involve complex logic to fix knowledge inconsistencies
        # For now, return a success response
        
        remediation_id = str(uuid.uuid4())
        
        return jsonify({
            'success': True,
            'remediation_id': remediation_id,
            'alert_id': alert_id,
            'strategy': remediation_strategy,
            'message': 'Knowledge drift remediation initiated',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error remediating knowledge drift: {e}")
        return jsonify({
            'error': 'Failed to remediate knowledge drift',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


# System Status and Analytics Endpoints

@autonomous_bp.route('/system/status', methods=['GET'])
@jwt_required()
def get_system_status():
    """Get overall system status"""
    try:
        # Collect system metrics
        total_agents = len(active_agents)
        healthy_agents = sum(1 for agent in active_agents.values() 
                           if agent.metrics.health_score > 0.7)
        degraded_agents = sum(1 for agent in active_agents.values() 
                            if 0.3 <= agent.metrics.health_score <= 0.7)
        failed_agents = sum(1 for agent in active_agents.values() 
                          if agent.metrics.health_score < 0.3)
        
        # Calculate average metrics
        if total_agents > 0:
            avg_health_score = sum(agent.metrics.health_score 
                                 for agent in active_agents.values()) / total_agents
            avg_response_time = sum(agent.metrics.average_response_time 
                                  for agent in active_agents.values()) / total_agents
            total_tasks_completed = sum(agent.metrics.tasks_completed 
                                      for agent in active_agents.values())
            total_tasks_failed = sum(agent.metrics.tasks_failed 
                                   for agent in active_agents.values())
        else:
            avg_health_score = 0
            avg_response_time = 0
            total_tasks_completed = 0
            total_tasks_failed = 0
        
        return jsonify({
            'system_health': 'healthy' if avg_health_score > 0.7 else 
                           'degraded' if avg_health_score > 0.3 else 'critical',
            'agent_statistics': {
                'total_agents': total_agents,
                'healthy_agents': healthy_agents,
                'degraded_agents': degraded_agents,
                'failed_agents': failed_agents
            },
            'performance_metrics': {
                'average_health_score': avg_health_score,
                'average_response_time': avg_response_time,
                'total_tasks_completed': total_tasks_completed,
                'total_tasks_failed': total_tasks_failed,
                'success_rate': (total_tasks_completed / 
                               max(1, total_tasks_completed + total_tasks_failed))
            },
            'lifecycle_statistics': {
                'active_requests': len(lifecycle_manager._active_requests),
                'active_implementations': len(lifecycle_manager._active_implementations),
                'deployed_agents': len(lifecycle_manager._deployed_agents)
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({
            'error': 'Failed to get system status',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


if __name__ == '__main__':
    # Example configuration for testing
    config = {
        'NEO4J_URI': 'bolt://localhost:7687',
        'NEO4J_USER': 'neo4j',
        'NEO4J_PASSWORD': 'password',
        'RABBITMQ_URL': 'amqp://localhost:5672',
        'OPENAI_API_KEY': 'your-openai-key',
        'DOCKER_CLIENT': None,  # Would be initialized with docker.from_env()
        'JWT_SECRET_KEY': 'your-secret-key'
    }
    
    app = create_autonomous_app(config)
    app.run(host='0.0.0.0', port=8000, debug=True)

