import { trigger, animate, style, group, animateChild, query, stagger, transition } from '@angular/animations';

export const routerTransition = trigger('routerTransition', [
    transition(`TutorialsPage => HomePage,
                StatisticsPage => IncidentPage,
                EventsPage => StatisticsPage,
                iCarePage => EventsPage,
                SponsorsPage => iCarePage,
                AboutPage => SponsorsPage,
                ContactUsPage => AboutPage,
                ContactUsPage => HomePage`, [
    /* order */
    /* 1 */ query(':enter, :leave',
                style({ position: 'fixed', width: '100%' }),
                { optional: true }),
    /* 2 */ group([  // block executes in parallel
            query(':enter', [
                    style({ transform: 'translateY(-100%)' }),
                    animate('0.5s ease-in-out', style({ transform: 'translateY(-0%)' }))
                ], { optional: true }),
            query(':leave', [
                    style({ transform: 'translateY(0%)' }),
                    animate('0.5s ease-in-out', style({ transform: 'translateY(+100%)' }))
                ], { optional: true })
            ])
    ]),
    transition(`HomePage => IncidentPage,
                IncidentPage => StatisticsPage,
                StatisticsPage => EventsPage,
                EventsPage => iCarePage,
                iCarePage => SponsorsPage,
                SponsorsPage => AboutPage,
                SponsorsPage => ContactUsPage,
                AboutPage => ContactUsPage`, [
        /* order */
        /* 1 */ query(':enter, :leave',
                    style({ position: 'fixed', width: '100%' }),
                    { optional: true }),
        /* 2 */ group([  // block executes in parallel
                query(':enter', [
                        style({ transform: 'translateY(100%)' }),
                        animate('0.5s ease-in-out', style({ transform: 'translateY(0%)' }))
                    ], { optional: true }),
                query(':leave', [
                        style({
                            bottom: '0',
                            transform: 'translateY(0%)'
                        }),
                        animate('0.5s ease-in-out', style({ transform: 'translateY(-100%)' }))
                    ], { optional: true })
                ])
        ])
]
);
