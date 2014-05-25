package eu.appbucket.queue.web.domain.office;

import eu.appbucket.queue.core.domain.queue.QueueDetails;
import eu.appbucket.queue.core.domain.queue.QueueInfo;
import eu.appbucket.queue.core.domain.queue.QueueStats;
import eu.appbucket.queue.web.domain.office.element.Address;
import eu.appbucket.queue.web.domain.office.element.ContactDetails;
import eu.appbucket.queue.web.domain.office.element.OpeningHours;

public class OfficeDetails {	
	
	private Address address;
	private OpeningHours openingHours;	
	private ContactDetails contactDetails;
	private String description; 
	
	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}
	public Address getAddress() {
		return address;
	}
	public void setAddress(Address address) {
		this.address = address;
	}
	public OpeningHours getOpeningHours() {
		return openingHours;
	}
	public void setOpeningHours(OpeningHours openingHours) {
		this.openingHours = openingHours;
	}
	public ContactDetails getContactDetails() {
		return contactDetails;
	}
	public void setContactDetails(ContactDetails contactDetails) {
		this.contactDetails = contactDetails;
	}
	
	public static OfficeDetails fromQueueData(
			QueueInfo queueInfo, QueueDetails queueDetails) {
		OfficeDetails officeDetails = new OfficeDetails();
		Address address = Address.fromQueuInfoAndAddress(queueInfo, queueDetails.getAddress());		
		officeDetails.setAddress(address);
		ContactDetails contactDetails = ContactDetails.fromQueueDetails(queueDetails);
		officeDetails.setContactDetails(contactDetails);
		OpeningHours openingHours = OpeningHours.fromOpeningHours(queueDetails.getOpeningHoursLocalTimeZone());
		officeDetails.setOpeningHours(openingHours);
		officeDetails.setDescription(queueDetails.getDescription());
		return officeDetails;
	}
}