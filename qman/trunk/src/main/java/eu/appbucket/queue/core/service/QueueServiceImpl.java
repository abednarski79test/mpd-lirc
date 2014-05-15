package eu.appbucket.queue.core.service;

import java.util.Calendar;
import java.util.Collection;
import java.util.Date;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import eu.appbucket.queue.core.domain.queue.OpeningHours;
import eu.appbucket.queue.core.domain.queue.OpeningTimes;
import eu.appbucket.queue.core.domain.queue.QueueDetails;
import eu.appbucket.queue.core.domain.queue.QueueInfo;
import eu.appbucket.queue.core.domain.queue.QueueStats;
import eu.appbucket.queue.core.persistence.QueueDao;
import eu.appbucket.queue.core.service.util.TimeGenerator;

@Service
public class QueueServiceImpl implements QueueService {
		
	private QueueDao queueDao;
	
	@Autowired
	public void setQueueDao(QueueDao queueDao) {
		this.queueDao = queueDao;
	}
	
	public Collection<QueueInfo> getQeueues() {
		Collection<QueueInfo> colleciton = queueDao.getQeueues();		
		return colleciton;
	}
	
	public QueueInfo getQueueInfoByQueueId(int queueId) {
		QueueInfo queueInfo= queueDao.getQueueInfoById(queueId);
		return queueInfo;
	}
	                  
	public QueueStats getQueueStatsByQueueId(int queueId) {
		Date todayAtMidnight = TimeGenerator.getTodayMidnightDate();
		QueueStats queueStats = queueDao.getQueueStatsByIdAndDate(queueId, todayAtMidnight);
		return queueStats;
	}
	
	protected long getAverageWaitingTime(int queueId) {
		QueueDetails queueDetails = this.getQueueDetailsByQueueId(queueId);
		int numberOfTicketPerDay = 200;
		long openingDuration = 
				queueDetails.getOpeningTimesUTC().getClosingTime() - queueDetails.getOpeningTimesUTC().getOpeningTime();
		long averageServiceTime = openingDuration / numberOfTicketPerDay;		
		return averageServiceTime;
	}
	
	public QueueDetails getQueueDetailsByQueueId(int queueId) {
		QueueDetails queueDetails= queueDao.getQueueDetailsById(queueId);
		OpeningTimes openingTimesUTC = calculateOpeningTime(queueDetails.getOpeningHoursUTC());
		queueDetails.setOpeningTimesUTC(openingTimesUTC);		
		return queueDetails;
	}
	
	public OpeningTimes calculateOpeningTime(OpeningHours openingHours) {
		OpeningTimes openingTime = new OpeningTimes();
		Calendar calendar = Calendar.getInstance();
		calendar.setTime(getNewDate());		
		calendar.set(Calendar.HOUR_OF_DAY, openingHours.getOpeningHour());
		calendar.set(Calendar.MINUTE, openingHours.getOpeningMinute());			
		calendar.set(Calendar.SECOND, 0);
		calendar.set(Calendar.MILLISECOND, 0);
		openingTime.setOpeningTime(calendar.getTimeInMillis());
		calendar.setTime(getNewDate());
		calendar.set(Calendar.HOUR_OF_DAY, openingHours.getClosingHour());
		calendar.set(Calendar.MINUTE, openingHours.getClosingMinute());
		calendar.set(Calendar.SECOND, 0);
		calendar.set(Calendar.MILLISECOND, 0);
		openingTime.setClosingTime(calendar.getTimeInMillis());			
		return openingTime;
	}
	
	protected Date getNewDate() {
		return new Date();
	}
	
	public void updateQueueStats(QueueStats queueStats) {
		queueDao.storeQueueStats(queueStats);	
	}
}
