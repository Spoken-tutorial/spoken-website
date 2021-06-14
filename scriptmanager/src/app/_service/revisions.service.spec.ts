import { TestBed } from '@angular/core/testing';

import { RevisionsService } from './revisions.service';

describe('RevisionsService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: RevisionsService = TestBed.get(RevisionsService);
    expect(service).toBeTruthy();
  });
});
