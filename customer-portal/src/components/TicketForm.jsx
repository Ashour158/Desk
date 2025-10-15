import React, { memo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import Logger from '../utils/logger';
import { useNotifications } from './NotificationSystem';
import EnhancedForm from './EnhancedForm';
import FormField from './FormField';
import { validationRules } from '../utils/formValidation';

/**
 * TicketForm component for creating new tickets
 * @param {Object} props - Component props
 * @param {Function} props.onSuccess - Callback when ticket is created successfully
 * @param {Object} props.initialData - Initial form data
 */
const TicketForm = memo(({ onSuccess, initialData = {} }) => {
  const navigate = useNavigate();
  const { showSuccess, showError, showWarning } = useNotifications();

  const [formInitialData] = useState({
    subject: '',
    description: '',
    priority: 'medium',
    category: '',
    channel: 'web',
    tags: '',
    custom_fields: {},
    ...initialData
  });

  /**
   * Custom validation rules for ticket form
   */
  const customValidationRules = {
    ...validationRules,
    category: [
      {
        type: 'required',
        message: 'Category is required',
        validate: (value) => value.trim() !== ''
      }
    ],
    priority: [
      {
        type: 'required',
        message: 'Priority is required',
        validate: (value) => value !== ''
      }
    ]
  };

  /**
   * Handle form submission
   * @param {Object} formData - Form data
   * @returns {Object} Submission result
   */
  const handleSubmit = async (formData) => {
    const startTime = performance.now();
    
    try {
      Logger.apiRequest('POST', '/api/v1/tickets/', { body: 'Present' });
      
      const response = await fetch('/api/v1/tickets/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(formData)
      });

      Logger.apiResponse('POST', '/api/v1/tickets/', response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      Logger.info('Ticket created successfully', {
        ticketId: data.id,
        subject: formData.subject,
        priority: formData.priority
      });
      
      Logger.userAction('ticket_created', {
        ticketId: data.id,
        subject: formData.subject,
        priority: formData.priority
      });

      // Show success notification
      showSuccess('Ticket created successfully!', {
        title: 'Success',
        message: `Ticket #${data.id} has been created and assigned to our support team.`,
        actions: [
          {
            label: 'View Ticket',
            onClick: () => navigate(`/tickets/${data.id}`)
          }
        ]
      });

      // Call success callback if provided
      if (onSuccess) {
        onSuccess(data);
      } else {
        navigate(`/tickets/${data.id}`);
      }
      
      return { success: true, data };
      
    } catch (error) {
      Logger.error('Error creating ticket:', error, {
        formData: {
          subject: formData.subject,
          priority: formData.priority,
          category: formData.category
        },
        status: error?.response?.status
      });
      
      // Handle different types of errors
      let errorMessage = 'An unexpected error occurred. Please try again.';
      
      if (error.message.includes('HTTP error')) {
        errorMessage = 'Server error. Please try again later.';
      } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessage = 'Network error. Please check your connection and try again.';
      }
      
      return { 
        success: false, 
        errors: { 
          general: errorMessage 
        } 
      };
    } finally {
      const duration = performance.now() - startTime;
      Logger.performance('createTicket', duration, {
        subject: formData.subject,
        priority: formData.priority
      });
    }
  };

  const getCsrfToken = () => {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'csrftoken') {
        return value;
      }
    }
    return '';
  };

  const handleTagChange = useCallback((e) => {
    const tags = e.target.value.split(',').map(tag => tag.trim()).filter(tag => tag);
    // This will be handled by the form validation system
  }, []);

  return (
    <div className="container-fluid">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="card">
            <div className="card-header">
              <h4 className="mb-0">Create New Ticket</h4>
            </div>
            <div className="card-body">
              <EnhancedForm
                formId="ticket-form"
                initialData={formInitialData}
                validationRules={customValidationRules}
                onSubmit={handleSubmit}
                options={{
                  enableAutoSave: true,
                  enableUnsavedChangesWarning: true,
                  enableAnalytics: true
                }}
              >
                {({ formData, errors, loading, getInputProps, getFieldError }) => (
                  <>
                    <div className="row">
                      <div className="col-md-6">
                        <FormField
                          name="subject"
                          label="Subject"
                          type="text"
                          required
                          placeholder="Brief description of your issue"
                          {...getInputProps('subject')}
                          error={getFieldError('subject')}
                        />
                      </div>
                      
                      <div className="col-md-3">
                        <FormField
                          name="priority"
                          label="Priority"
                          type="select"
                          required
                          options={[
                            { value: 'low', label: 'Low' },
                            { value: 'medium', label: 'Medium' },
                            { value: 'high', label: 'High' },
                            { value: 'urgent', label: 'Urgent' }
                          ]}
                          {...getInputProps('priority')}
                          error={getFieldError('priority')}
                        />
                      </div>
                      
                      <div className="col-md-3">
                        <FormField
                          name="category"
                          label="Category"
                          type="select"
                          required
                          options={[
                            { value: '', label: 'Select Category' },
                            { value: 'technical', label: 'Technical Support' },
                            { value: 'billing', label: 'Billing' },
                            { value: 'general', label: 'General Inquiry' },
                            { value: 'feature', label: 'Feature Request' },
                            { value: 'bug', label: 'Bug Report' }
                          ]}
                          {...getInputProps('category')}
                          error={getFieldError('category')}
                        />
                      </div>
                    </div>

                    <div className="row">
                      <div className="col-12">
                        <FormField
                          name="description"
                          label="Description"
                          type="textarea"
                          required
                          rows={6}
                          placeholder="Please provide detailed information about your issue..."
                          helpText="Include steps to reproduce, error messages, and any relevant details"
                          {...getInputProps('description')}
                          error={getFieldError('description')}
                        />
                      </div>
                    </div>

                    <div className="row">
                      <div className="col-md-6">
                        <FormField
                          name="tags"
                          label="Tags (Optional)"
                          type="text"
                          placeholder="Enter tags separated by commas"
                          helpText="Add relevant tags to help categorize your ticket"
                          {...getInputProps('tags')}
                          error={getFieldError('tags')}
                        />
                      </div>
                      
                      <div className="col-md-6">
                        <FormField
                          name="channel"
                          label="Contact Channel"
                          type="select"
                          options={[
                            { value: 'web', label: 'Web Portal' },
                            { value: 'email', label: 'Email' },
                            { value: 'phone', label: 'Phone' },
                            { value: 'chat', label: 'Live Chat' }
                          ]}
                          {...getInputProps('channel')}
                          error={getFieldError('channel')}
                        />
                      </div>
                    </div>

                    {/* Custom Fields Section */}
                    <div className="row">
                      <div className="col-12">
                        <h5 className="mt-4 mb-3">Additional Information</h5>
                        <div className="row">
                          <div className="col-md-6">
                            <FormField
                              name="custom_fields.urgency"
                              label="Urgency Level"
                              type="select"
                              options={[
                                { value: '', label: 'Select Urgency' },
                                { value: 'low', label: 'Low - Can wait' },
                                { value: 'medium', label: 'Medium - Within 24 hours' },
                                { value: 'high', label: 'High - Within 4 hours' },
                                { value: 'critical', label: 'Critical - Immediate' }
                              ]}
                              {...getInputProps('custom_fields.urgency')}
                              error={getFieldError('custom_fields.urgency')}
                            />
                          </div>
                          
                          <div className="col-md-6">
                            <FormField
                              name="custom_fields.environment"
                              label="Environment"
                              type="select"
                              options={[
                                { value: '', label: 'Select Environment' },
                                { value: 'production', label: 'Production' },
                                { value: 'staging', label: 'Staging' },
                                { value: 'development', label: 'Development' },
                                { value: 'test', label: 'Test' }
                              ]}
                              {...getInputProps('custom_fields.environment')}
                              error={getFieldError('custom_fields.environment')}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </EnhancedForm>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});

TicketForm.propTypes = {
  onSuccess: PropTypes.func,
  initialData: PropTypes.object
};

TicketForm.defaultProps = {
  onSuccess: null,
  initialData: {}
};

export default TicketForm;