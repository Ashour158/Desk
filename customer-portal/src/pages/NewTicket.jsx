import React from 'react';
import TicketForm from '../components/TicketForm';
import PropTypes from 'prop-types';

/**
 * New ticket page component
 * @param {Object} props - Component props
 */
const NewTicket = ({ user }) => {
  return (
    <div className="space-y-6">
      <div className="md:flex md:items-center md:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Create New Ticket
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Submit a new support request
          </p>
        </div>
      </div>

      <TicketForm user={user} />
    </div>
  );
};

NewTicket.propTypes = {
  user: PropTypes.shape({
    id: PropTypes.number,
    first_name: PropTypes.string,
    last_name: PropTypes.string,
    email: PropTypes.string,
  }),
};

NewTicket.defaultProps = {
  user: null,
};

export default NewTicket;
