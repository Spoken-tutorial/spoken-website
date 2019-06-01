import { Component, OnInit } from '@angular/core';
import { TutorialsService } from '../../_service/tutorials.service'
@Component({
  selector: 'app-tutorials',
  templateUrl: './tutorials.component.html',
  styleUrls: ['./tutorials.component.sass']
})
export class TutorialsComponent implements OnInit {
  public tutorials;
  constructor(public apiService: TutorialsService){
    this.tutorials = this.apiService.getTutorials();
  }

  ngOnInit() {
  }

}
