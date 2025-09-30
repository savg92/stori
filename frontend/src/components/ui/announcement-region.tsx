import React from 'react';

interface AnnouncementRegionProps {
	announceRef: React.RefObject<HTMLDivElement>;
}

export function AnnouncementRegion({ announceRef }: AnnouncementRegionProps) {
	return (
		<div
			ref={announceRef}
			aria-live='polite'
			aria-atomic='true'
			className='sr-only'
		/>
	);
}
