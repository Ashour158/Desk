import React from 'react';
import TicketList from '../components/TicketList';
import PropTypes from 'prop-types';

/**
 * Tickets page component
 * @param {Object} props - Component props
 */
const Tickets = ({ user }) => {
  return (
    <div className="space-y-6">
      <div className="md:flex md:items-center md:justify-between">
        <div className="flex-1 min-w-0">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            My Tickets
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            View and manage all your support tickets
          </p>
        </div>
      </div>

      <TicketList user={user} />
    </div>
  );
};

Tickets.propTypes = {
  user: PropTypes.shape({
    id: PropTypes.number,
    first_name: PropTypes.string,
    last_name: PropTypes.string,
    email: PropTypes.string,
  }),
};

Tickets.defaultProps = {
  user: null,
};

export default Tickets;
