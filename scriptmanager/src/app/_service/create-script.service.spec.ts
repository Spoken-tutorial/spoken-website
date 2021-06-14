import { TestBed } from '@angular/core/testing';

import { CreateScriptService } from './create-script.service';

describe('CreateScriptService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: CreateScriptService = TestBed.get(CreateScriptService);
    expect(service).toBeTruthy();
  });
});
