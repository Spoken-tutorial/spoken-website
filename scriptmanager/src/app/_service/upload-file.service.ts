import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class UploadFileService {
public testData:FormData = new FormData();

public postFile(tid,file){

  this.testData.append('file_upload',tid,file );
  return this.http.post('https://url', this.testData);
}
  constructor(public http:HttpClient) { }
}
