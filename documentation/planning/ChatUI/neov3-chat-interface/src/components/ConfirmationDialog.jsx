import React from 'react';
import { AlertTriangle, Info, CheckCircle, XCircle, X } from 'lucide-react';
import { Button } from './ui/button';

const ConfirmationDialog = ({ 
  title, 
  message, 
  type = 'info', 
  onConfirm, 
  onCancel,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  details = null,
  impact = null
}) => {
  const getIcon = () => {
    switch (type) {
      case 'danger': return <XCircle className="w-6 h-6 text-red-500" />;
      case 'warning': return <AlertTriangle className="w-6 h-6 text-amber-500" />;
      case 'success': return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'info':
      default: return <Info className="w-6 h-6 text-blue-500" />;
    }
  };

  const getButtonVariant = () => {
    switch (type) {
      case 'danger': return 'destructive';
      case 'warning': return 'default';
      case 'success': return 'default';
      case 'info':
      default: return 'default';
    }
  };

  return (
    <div className="dialog-overlay animate-fade-in">
      <div className="dialog-content animate-slide-in">
        {/* Header */}
        <div className="dialog-header">
          {getIcon()}
          <div className="flex-1">
            <h3 className="dialog-title">{title}</h3>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onCancel}
            className="w-6 h-6 p-0"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="space-y-4">
          <p className="text-sm text-foreground leading-relaxed">
            {message}
          </p>

          {/* Additional Details */}
          {details && (
            <div className="p-3 bg-muted rounded-lg">
              <h4 className="text-sm font-medium text-foreground mb-2">Details:</h4>
              <div className="text-sm text-muted-foreground space-y-1">
                {Array.isArray(details) ? (
                  details.map((detail, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <span className="w-1 h-1 bg-muted-foreground rounded-full mt-2 flex-shrink-0"></span>
                      <span>{detail}</span>
                    </div>
                  ))
                ) : (
                  <p>{details}</p>
                )}
              </div>
            </div>
          )}

          {/* Impact Analysis */}
          {impact && (
            <div className={`p-3 rounded-lg ${
              type === 'danger' ? 'bg-red-50 border border-red-200' :
              type === 'warning' ? 'bg-amber-50 border border-amber-200' :
              'bg-blue-50 border border-blue-200'
            }`}>
              <h4 className="text-sm font-medium text-foreground mb-2">
                {type === 'danger' ? 'Impact of this action:' : 'This will:'}
              </h4>
              <div className="text-sm space-y-1">
                {Array.isArray(impact) ? (
                  impact.map((item, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <span className={`w-1 h-1 rounded-full mt-2 flex-shrink-0 ${
                        type === 'danger' ? 'bg-red-500' :
                        type === 'warning' ? 'bg-amber-500' :
                        'bg-blue-500'
                      }`}></span>
                      <span className={
                        type === 'danger' ? 'text-red-700' :
                        type === 'warning' ? 'text-amber-700' :
                        'text-blue-700'
                      }>{item}</span>
                    </div>
                  ))
                ) : (
                  <p className={
                    type === 'danger' ? 'text-red-700' :
                    type === 'warning' ? 'text-amber-700' :
                    'text-blue-700'
                  }>{impact}</p>
                )}
              </div>
            </div>
          )}

          {/* Warning for destructive actions */}
          {type === 'danger' && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-500 flex-shrink-0" />
                <p className="text-sm text-red-700 font-medium">
                  This action cannot be undone
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="dialog-actions">
          <Button
            variant="outline"
            onClick={onCancel}
          >
            {cancelText}
          </Button>
          <Button
            variant={getButtonVariant()}
            onClick={onConfirm}
          >
            {confirmText}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationDialog;

