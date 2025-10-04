import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import Badge from '../ui/Badge';
import ProgressBar from './ProgressBar';
import Spinner from './Spinner';
import { CheckCircle2, XCircle, Clock, AlertCircle } from 'lucide-react';

export type TaskState = 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE' | 'RETRY';

export interface TaskStatusData {
  taskId: string;
  state: TaskState;
  progress?: number;
  result?: Record<string, unknown>;
  error?: string;
  message?: string;
  startedAt?: string;
  completedAt?: string;
}

export interface TaskStatusProps {
  task: TaskStatusData;
  title?: string;
  className?: string;
}

const TaskStatus: React.FC<TaskStatusProps> = ({ task, title = 'Task Status', className }) => {
  const getStatusIcon = () => {
    switch (task.state) {
      case 'SUCCESS':
        return <CheckCircle2 className="text-green-600" size={24} />;
      case 'FAILURE':
        return <XCircle className="text-red-600" size={24} />;
      case 'RETRY':
        return <AlertCircle className="text-yellow-600" size={24} />;
      case 'PENDING':
        return <Clock className="text-gray-600" size={24} />;
      case 'STARTED':
        return <Spinner size="sm" color="blue" />;
      default:
        return <Clock className="text-gray-600" size={24} />;
    }
  };

  const getStatusBadge = () => {
    switch (task.state) {
      case 'SUCCESS':
        return <Badge variant="success">Completed</Badge>;
      case 'FAILURE':
        return <Badge variant="error">Failed</Badge>;
      case 'RETRY':
        return <Badge variant="warning">Retrying</Badge>;
      case 'PENDING':
        return <Badge variant="default">Pending</Badge>;
      case 'STARTED':
        return <Badge variant="info">In Progress</Badge>;
      default:
        return <Badge variant="default">{task.state}</Badge>;
    }
  };

  const getProgressColor = (): 'blue' | 'green' | 'yellow' | 'red' => {
    switch (task.state) {
      case 'SUCCESS':
        return 'green';
      case 'FAILURE':
        return 'red';
      case 'RETRY':
        return 'yellow';
      default:
        return 'blue';
    }
  };

  return (
    <Card variant="bordered" className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            {getStatusIcon()}
            {title}
          </CardTitle>
          {getStatusBadge()}
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {/* Task ID */}
          <div>
            <p className="text-xs text-gray-500 mb-1">Task ID</p>
            <p className="text-sm font-mono text-gray-700 break-all">{task.taskId}</p>
          </div>

          {/* Progress Bar */}
          {task.state === 'STARTED' && task.progress !== undefined && (
            <ProgressBar
              value={task.progress}
              label="Progress"
              color={getProgressColor()}
            />
          )}

          {/* Message */}
          {task.message && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-sm text-gray-700">{task.message}</p>
            </div>
          )}

          {/* Error */}
          {task.error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-sm font-medium text-red-900 mb-1">Error</p>
              <p className="text-sm text-red-700">{task.error}</p>
            </div>
          )}

          {/* Result */}
          {task.state === 'SUCCESS' && task.result && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
              <p className="text-sm font-medium text-green-900 mb-2">Result</p>
              <pre className="text-xs text-green-800 overflow-x-auto">
                {JSON.stringify(task.result, null, 2)}
              </pre>
            </div>
          )}

          {/* Timestamps */}
          <div className="flex items-center justify-between text-xs text-gray-500">
            {task.startedAt && (
              <span>Started: {new Date(task.startedAt).toLocaleString()}</span>
            )}
            {task.completedAt && (
              <span>Completed: {new Date(task.completedAt).toLocaleString()}</span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default TaskStatus;
