package eu.appbucket.queue.core.mock;

import java.util.Calendar;
import java.util.Date;
import java.util.Random;

import eu.appbucket.queue.core.domain.queue.Address;
import eu.appbucket.queue.core.domain.queue.GeographicalLocation;
import eu.appbucket.queue.core.domain.queue.OpeningTimes;
import eu.appbucket.queue.core.domain.queue.QueueDetails;
import eu.appbucket.queue.core.domain.queue.QueueStats;

public class QueueMockDataGenerater {
	
	public static QueueStats generateMockQueueStats() {
		QueueStats queueStats = new QueueStats();
		Random randomGenerator = new Random();
		int nuberOfMilisecondsIn8hours = 28800000;
		queueStats.setCalculatedAverageWaitingDuration(randomGenerator.nextInt(nuberOfMilisecondsIn8hours));
		return queueStats;
	}
	
	public static QueueDetails generateMockQueueDetails() {
		QueueDetails queueDetails = new QueueDetails();		
		Address address = new Address();
		address.setAddressLine1("Adress line 1");
		address.setAddressLine2("Adress line 2");
		address.setCountry("Republic Of Irlenad");
		address.setCounty("Dublin");
		address.setPostcode("D1");
		address.setTownOrCity("Dublin");
		queueDetails.setAddress(address);
		GeographicalLocation location = new GeographicalLocation();
		location.setLatitude(53.347778F);
		location.setLongitude(-6.259722F);
		queueDetails.setLocation(location);
		OpeningTimes openingTimes = new OpeningTimes();
		Calendar calendar = Calendar.getInstance();
		calendar.setTime(new Date());
		calendar.set(Calendar.HOUR, 9);
		calendar.set(Calendar.MINUTE, 30);
		openingTimes.setOpeningTime(calendar.getTimeInMillis());
		calendar.setTime(new Date());
		calendar.set(Calendar.HOUR, 17);
		calendar.set(Calendar.MINUTE, 30);
		openingTimes.setClosingTime(calendar.getTimeInMillis());
		queueDetails.setOpeningTimesUTC(openingTimes);		
		queueDetails.setPhoneNumber("016669100");
		queueDetails.setEmail("gnib_dv@garda.ie");
		return queueDetails;
	}
}
