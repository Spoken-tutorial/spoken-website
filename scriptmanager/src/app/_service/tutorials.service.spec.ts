import { TestBed } from '@angular/core/testing';

import { TutorialsService } from './tutorials.service';

describe('TutorialsService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: TutorialsService = TestBed.get(TutorialsService);
    expect(service).toBeTruthy();
  });
});
