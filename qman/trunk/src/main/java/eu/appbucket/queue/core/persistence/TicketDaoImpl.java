package eu.appbucket.queue.core.persistence;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Collection;
import java.util.Date;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.core.simple.SimpleJdbcTemplate;
import org.springframework.stereotype.Repository;

import eu.appbucket.queue.core.domain.queue.QueueInfo;
import eu.appbucket.queue.core.domain.ticket.TicketUpdate;

@Repository
public class TicketDaoImpl implements TicketDao {
	
	private final static String SQL_INSERT_TICKET_UPDATE = 
			"INSERT INTO updates(`queue_id`, `user_ticket`, `served_ticket`, `created`, `is_valid`) "
			+ "VALUES (?, ?, ?, ?, 1)";
	
	private final static String SQL_SELECT_TICKET_UPDATES_BY_QUEUE_AND_TIMESTAMP = 
			"SELECT * FROM updates WHERE queue_id = ? AND created >= ? AND created <= ?";
	
	private SimpleJdbcTemplate jdbcTempalte;
	
	@Autowired
	public void setJdbcTempalte(SimpleJdbcTemplate jdbcTempalte) {
		this.jdbcTempalte = jdbcTempalte;
	}
	
	public void storeTicketUpdate(TicketUpdate ticketUpdate) {
		jdbcTempalte.update(SQL_INSERT_TICKET_UPDATE, 
				ticketUpdate.getQueueInfo().getQueueId(),
				ticketUpdate.getClientTicketNumber(),
				ticketUpdate.getCurrentlyServicedTicketNumber(),
				ticketUpdate.getCreated());		
	}
	
	public Collection<TicketUpdate> readTicketUpdatesByQueueAndTimeStamp(QueueInfo queueInfo, Date fromDate, Date toDate) {		
		Collection<TicketUpdate> ticketUpdates = jdbcTempalte.query(
				SQL_SELECT_TICKET_UPDATES_BY_QUEUE_AND_TIMESTAMP, 
				new TicketUpdateMapper(),
				queueInfo.getQueueId(), fromDate, toDate);
		return ticketUpdates;
	}

	private static final class TicketUpdateMapper implements RowMapper<TicketUpdate> {
		public TicketUpdate mapRow(ResultSet rs, int rowNum) throws SQLException {
			TicketUpdate ticketUpdate = new TicketUpdate();
			QueueInfo queueInfo = new QueueInfo();
			queueInfo.setQueueId(rs.getInt("queue_id"));
			ticketUpdate.setQueueInfo(queueInfo);
			ticketUpdate.setClientTicketNumber(rs.getInt("user_ticket"));
			ticketUpdate.setCurrentlyServicedTicketNumber(rs.getInt("served_ticket"));
			ticketUpdate.setCreated(rs.getTimestamp("created"));
			return ticketUpdate;
		}		
	}
}
